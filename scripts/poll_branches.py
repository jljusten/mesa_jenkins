import sys, os, urllib2, time
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), ".."))
import build_support as bs

status = bs.RepoStatus()

pm = bs.ProjectMap()
spec = pm.build_spec()
server = spec.find("build_master").attrib["host"]
while True:
    branches = status.poll()
    for (branch, commit) in branches.iteritems():
        print "Building " + branch
        job_url = "http://" + server + "/job/" + branch + \
                  "/buildWithParameters?token=xyzzy&name=" + commit + "&type=percheckin"
        retry_count = 0
        while retry_count < 10:
            try:
                f = urllib2.urlopen(job_url)
                f.read()
                break
            except urllib2.HTTPError as e:
                print e
                retry_count = retry_count + 1
                print "ERROR: failed to reach jenkins, retrying: " + job_url
                time.sleep(10)

    time.sleep(60)
