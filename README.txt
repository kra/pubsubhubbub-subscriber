PubSubHubBub subscriber by Karl Anderson.


Setup/config:

Have a file with feed URLs, one per line.  An included example is the
feed_urls file.
Edit conf.py, see comments.
Note that the process must be restarted if the values in conf.py are changed.


Deploy:

Launch a Fedora Core 8 EC2 instance.  I used the micro instance type
for testing. Make sure the SSH port and port 80 (or whatever is
appropriate for your conf.py value) are open in the firewall. Note the
public DNS address so you can SSH in and copy files over.

Copy code to the instance using your Amazon AWS private key.
Substitute the public DNS address for your instance for this and
future examples.

    scp -Cr -i aws/foo.pem  pshb 'root@ec2-184-72-164-138.compute-1.amazonaws.com:/tmp'


Run:

SSH into the instance and run the uploaded script.

    ssh root@ec2-184-72-164-138.compute-1.amazonaws.com -i foo.pem 
    cd /tmp/pshb
    python -u run.py

Of course, you can bake the source into an EC2 AMI; if you do that,
you probably want to install the included pubsubhubbub library using
setuptools.
        

Performance notes:

For several thousand feeds on a small EC2 instance, the bottleneck is
the remote publisher.

For production, you will want to parallelize this simply because
subscribing takes time on startup - about 0.5 seconds per sub, again
due to the remote publisher.  The
easiest way to parallelize is to run seperate processes on the same or
separate EC2 instances, each with their own disjoint list of subs,
writing to the same store.  Other ways to parallelize would be to
subscribe and publish in several threads (would have to make some
thread-safety edits), or to cluster behind a loadbalancer among
processes or EC2 instances, each with their own local_port.
Clustering would require some code to make sure that a subscriber knew
what to do with an incoming callback from the publisher, but would be
the most appealing way to scale because the subscriber and receiver
could be separate, avoiding the subscription delay in startup.


Software/requriements:

pubsubhubbub.py is copied from my fork of an open source Python
pubsubhubbub subscriber:

    http://bitbucket.org/kra/pubsubhubbub

The entire source tree is included in the 'pubsubhubbub' directory.
You could, of course, install this on your instance with mercurial, or
make a RPM; I just included the source file for ease of prototyping.
Be sure to read the license if you intend to distribute source or
executables.

Testing was done on an Amazon-supplied basic Fedora Core 8 AMI
instance.
