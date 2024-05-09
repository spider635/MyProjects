import os
import sys
import asyncio 
import requests
import datetime
import time
import re
import csv
import json
import argparse
import xml.etree.ElementTree as ET

MAX_TASK = 8
CON_TIMEOUT = 10
CACHE_FOLDER = 'cache'
CACHE_AUTOSAVE = 100

USER_AGENT_HEADER="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

def get_prop( id, ts=0 ):
    url = 'https://api.domain.com.au/v1/property-details/{}'.format( id )

    try:
        r = requests.get( url, timeout=CON_TIMEOUT, headers={"User-Agent": USER_AGENT_HEADER})
        d = r.json()

    except Exception as msg:
        print( f'error: {url} => {msg}')
        return None

    # suburb & postcode
    a = d.get('metadata',{}).get('address_components',{})

    # Add a one-second delay before returning the result
    time.sleep(0.5)
    
    o = [
        ts, id,
        d.get('dwelling_type',''),
        d.get('address',''),
        a.get('state_short',''),
        a.get('suburb',''),
        a.get('postcode',''),
        d.get('lifecycle_status',''),
        '',
        '',
        int(d.get('bathroom_count',0)),
        int(d.get('bedroom_count',0)),
        int(d.get('carspace_count',0)),
        d.get('area',''),
        (', ').join( d.get('additional_features',[]) ),
        d.get('media',[{}])[0].get('image_url',''),
        d.get('seo_url',''),
        d.get('description','')
    ]

    # mode
    o[ 8 if d.get('search_mode','').lower() != 'rent' else 9 ] = d.get('price','')
    return o

async def prop_init( que, index, cache, f_cache, t_out ):
    queue = asyncio.Queue( )
    for a in que: await queue.put( a )
    
    run = [ asyncio.create_task( prop_task( queue, index, cache, f_cache, t_out ) ) 
            for n in range(MAX_TASK) ]
    await asyncio.gather( *run )
    
    # save cache:
    if prop_stat.counter > 0: await prop_write(cache, f_cache)
                            
async def prop_task( queue, index, cache, f_cache, t_out ):
    while not queue.empty( ) and not prop_stat.done:
        r = await queue.get( )
        a = index[r['id']] = cache[r['id']] = await asyncio.get_event_loop( ).run_in_executor( None, get_prop, r['id'], r['ts'] )
        if a == None:
            prop_stat( err_inc=1 )
        else:
            prop_stat( num_inc=1 )
            # csv:
            if (( not args.states ) or ( a[4].upper() in args.states )):
                async with asyncio.Lock(): t_out.writerow( a[1:] )
                prop_stat.total += 1
                if args.count and (prop_stat.total >= args.count): prop_stat.done = True
                
            # save cache:
            prop_stat.counter += 1
            if prop_stat.counter >= CACHE_AUTOSAVE:
                await prop_write(cache, f_cache)
                prop_stat.counter = 0

            # Add a 1.0 second delay before processing the next record
            # await asyncio.sleep(1.0)
        
async def prop_write(cache, f_cache):
    async with asyncio.Lock():
        f_cache.seek(0)
        f_cache.write( json.dumps( cache, indent='\t', separators=(',',':') ) )
        f_cache.truncate()

def prop_stat( toc_set=None, toc_inc=0, num_set=None, num_inc=0, num_tot=0, err_set=None, err_inc=0, init=False ):
    if init:
        prop_stat.done = False
        prop_stat.total = 0
        prop_stat.counter = 0
        prop_stat.num = [0,0]
        prop_stat.toc = [0,0]
        prop_stat.err = 0

    if toc_set: prop_stat.toc = toc_set
    if toc_inc: prop_stat.toc[0] += toc_inc
    
    if num_set: prop_stat.num = num_set
    if num_inc: prop_stat.num[0] += num_inc
    if num_tot: prop_stat.num[1] += num_tot
    
    if err_set: prop_stat.err = 0
    if err_inc: prop_stat.err += err_inc
    
    print_progress( f'    files: {prop_stat.toc[0]}/{prop_stat.toc[1]} records: {prop_stat.num[0]}/{prop_stat.num[1]} errors: {prop_stat.err} results: {prop_stat.total}' )

def update_lists( ):
    # index:
    if args.mode == 'sale':
        u = 'https://www.domain.com.au/sitemap-listings-sale.xml'
    elif args.mode == 'rent':
        u = 'https://www.domain.com.au/sitemap-listings-rent.xml'
    else:
        return False

    print( ' Downloading updates ...' )    
    # print(requests.get(f'{u}?ts={time.time()}', headers={"User-Agent": USER_AGENT_HEADER}).text)
    ret = { e[0].text:e[1].text for e in ET.fromstring(requests.get(f'{u}?ts={time.time()}', headers={"User-Agent": USER_AGENT_HEADER}).text) }
    
    s = f'{CACHE_FOLDER}/index.json'
    if os.path.isfile(s) and os.path.getsize(s):
        with open(s,'r') as f: cur = json.load(f)
    else:
        cur = {}
        
    # database:
    for i,u in enumerate(ret,start=1):
        n = os.path.basename(u)
        p = f'{CACHE_FOLDER}/{n}'
        t = ret.get(u,'')
        
        if ( not os.path.isfile(p) ) or ( cur.get(u,'') != t ):
            r = requests.get(u, stream=True, headers={"User-Agent": USER_AGENT_HEADER})
            o = int(r.headers.get('content-length',0))
            c = 0
            with open(p,'w+b') as f:
                for b in r.iter_content(2048*256):
                    f.write(b)
                    c += len(b)
                    print_progress( f'    files: {i}/{len(ret)} size: {c/1048576:.2f}/{o/1048576:.2f}MB' )
            #
            cur[u] = t
            with open(s,'w+') as f: json.dump(cur,f,indent=4)
    
    print_progress( f'    {len(ret)} files downloaded\n' )
    
    return ret

def print_progress( txt ):
    print( f'\033[2K\r{txt}', end='')

def parse_args( ):
    p = argparse.ArgumentParser(
        prog='domain',
        formatter_class=argparse.RawTextHelpFormatter,
        #description='Parse (sale/rent/etc.) properties data from https://domain.com.au',
        epilog=('\n').join([
            'Examples:',
            '   %(prog)s sale data-sale.csv',
            '   %(prog)s sale data-sale.csv --count 100',
            '   %(prog)s rent data-rent.csv --states NSW',
            '   %(prog)s rent data-rent.csv --states NSW VIC --count 2000',
            ' '
        ])
    )
    p.add_argument( 'mode', choices=['sale','rent'], help='search mode' )
    p.add_argument( 'output', type=str, help='output file (csv)' )
    p.add_argument( '--states', type=str, nargs='+', help='filter results by states' )
    p.add_argument( '--count', type=int, help='limit results count',  )
    #p.add_argument( '-n', dest='noupdate', action='store_true', help='disable auto update' )
    a = p.parse_args()
    if a.states: a.states = [e.upper() for e in a.states]
    return a
    
def main():
    reg = re.compile('(\d+)$')

    # UPDATE LISTS:
    doc = update_lists()
    
    # UPDATE RECORDS:
    print( ' Updating records ...' )    
    prop_stat( init=True, toc_set=[0,len(doc)] ) 

    with open( args.output, 'w+', encoding='utf-8-sig', newline='') as f_out:
        t_out = csv.writer( f_out, delimiter=',', quoting=csv.QUOTE_ALL )
        t_out.writerow(['ID','Type','Address','State','Suburb','Postcode','Status','Buy','Rent','Bathroom','Bedroom','Carspace','Size',
                        'Features','Image','Url','Description'])

        for u in doc:
            if prop_stat.done: break
            prop_stat( toc_inc=1 )
            n = os.path.basename(u)
            p = f'{CACHE_FOLDER}/{os.path.basename(u)}'
            
            if os.path.isfile(p):
                # cache:               
                s = f'{CACHE_FOLDER}/{os.path.splitext(os.path.basename(u))[0]}.json'
                
                index = {}

                if os.path.isfile(s) and os.path.getsize(s):
                    with open(s,'r') as f: cache = json.load(f)       
                else:
                    cache = {}
                
                # queue:
                que = []
                rec = ET.parse(p).getroot()
                prop_stat( num_tot=len(rec) )
                
                for o in rec:
                    if prop_stat.done: break
                    h = reg.search( o[0].text )
                    if h:
                        t = datetime.datetime.fromisoformat(o[1].text).timestamp()
                        if ( h[0] in cache ) and ( cache[h[0]] != None ) and (cache[h[0]][0] == t):
                            prop_stat( num_inc=1 )
                        else:
                            cache[h[0]] = None
                            que.append( {'id':h[0], 'ts':t} )

                        a = index[h[0]] = cache[h[0]]
                        if a:
                            if (( not args.states ) or ( a[4].upper() in args.states )):
                                t_out.writerow( a[1:] )
                                prop_stat.total += 1
                                if args.count and (prop_stat.total >= args.count): prop_stat.done = True
                                    
                # fetch:
                if len(que):
                    with open(s,'w+') as f_cache:
                        asyncio.run( prop_init( que, index, cache, f_cache, t_out ) )
           
            #break
    #
    prop_stat()
    print( f'\n\n Total results: {prop_stat.total} records' )

# begin:
if __name__ == '__main__':
    os.makedirs(CACHE_FOLDER,exist_ok=True)
    print( )
    args = parse_args( )
    print( 
        f' Output mode: {args.mode} file: {args.output}',
        'states: {}'.format(', '.join(args.states)) if args.states else ''
    )
    print( )

    main( )
    print( ' Done.\n' )
