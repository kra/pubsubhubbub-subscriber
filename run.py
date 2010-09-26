import os, datetime, sys, logging
# req. http://bitbucket.org/pstatic/pubsubhubbub/wiki/Home
import pubsubhubbub
import conf


# Note no filtering of duplicates, which might happen after a restart.
def write_sub((sub, update_data)):
    """Stub for storing a received subcription update."""
    print '%s write_sub sub: %s' % (datetime.datetime.now(), sub)
    #print '%s write_sub data: %s' % (datetime.datetime.now(), update_data)

def get_hostname():
    """Return a string with the public hostname of this EC2 instance."""
    (fin, fout) = os.popen4(
        "wget -q -O - "
        "http://instance-data.ec2.internal/latest/meta-data/public-hostname")
    return fout.read().strip()

def feed_urls(feed_url_filename):
    """
    Yield feed URLs read from file in WD named feed_url_filename.
    URLS must be one per line.
    """
    f = open(feed_url_filename)
    for line in f.readlines():
        yield line.strip()
    f.close()

def start_server(feed_urls, local_address, local_port):
    """Return a server subscribed to feed_urls."""
    bind_addr = (local_address, local_port)
    pshb = pubsubhubbub.PubSubHubbub(bind_addr, autostart_server=True)
    
    for feed_url in feed_urls:
        # Get and subscribe to a PuSHSubscriptionInfo object.
        try:
            logging.getLogger('pubsubhubbub').debug("feed URL %s" % feed_url)
            sub_info = pubsubhubbub.subscription_from_url(feed_url)
            logging.getLogger('pubsubhubbub').debug(
                "Hub URL %s" % sub_info.hub_url)
        except:
            logging.getLogger('pubsubhubbub').warning(
                "Could not find subscription for feed URL %s" % feed_url)
        else:
            try:
                pshb.subscribe(sub_info)
            except pubsubhubbub.PuSHException, exc:
                logging.getLogger('pubsubhubbub').warning(
                    "Could not subscribe for feed URL %s" % feed_url)
            except Exception, exc:
                logging.getLogger('pubsubhubbub').error(
                    "Unknown error subscribing to feed URL %s" % feed_url)
        
    return pshb

def run_server(pshb):
    """
    Receive updates from the given server's subscriptions indefinately,
    in a single thread.
    """
    # the library will handle automatic sub refreshing
    while True:
        data = pshb.wait_for_updates(conf.update_secs)
        for item in data:
            write_sub(item)

def setup_logging(level):
    l = logging.getLogger('pubsubhubbub')
    l.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    l.addHandler(handler)

if __name__ == "__main__":
    setup_logging(conf.log_level)
    # address and port for publisher to call back to us
    local_address = get_hostname()
    local_port = conf.local_port
    # filename of feed URLs which refer to hub links, one per line
    feed_url_filename = 'feed_urls'

    run_server(start_server(
        feed_urls(conf.feed_url_filename), local_address, local_port))
