"""utils to centralize global variabl settings configurable by env vars."""
import os

# envs that can be override by os.environ envs
GSHOSTNAME = 'localhost'
GSPORT = '8080'
GSSSHPORT = '8443'
GSUSER = 'admin'
GSPASSWORD = 'geoserver'


def geoserverLocation():
    """get GSHOSTNAME and GSPORT or use default localhost:8080."""
    server = GSHOSTNAME
    port = GSPORT
    server = os.getenv('GSHOSTNAME', server)
    port = os.getenv('GSPORT', port)
    return '%s:%s' % (server, port)


def geoserverLocationSsh():
    """get GSSSHPORT and GSSSHPORT or use default localhost:8443."""
    location = geoserverLocation().split(":")[0]
    sshport = GSSSHPORT
    sshport = os.getenv('GSSSHPORT', sshport)
    return '%s:%s' % (location, sshport)


def serverLocationBasicAuth():
    """Set server URL for http connection."""
    return "http://"+geoserverLocation()+"/geoserver"


def serverLocationPkiAuth():
    """Set server URL for https connection."""
    return "https://"+geoserverLocationSsh()+"/geoserver"


GSPARAMS = dict(
    GSURL=serverLocationBasicAuth()+'/rest',
    GSUSER=GSUSER,
    GSPASSWORD=GSPASSWORD,
    GEOSERVER_HOME='',
    DATA_DIR='',
    GS_VERSION='',
    GS_BASE_DIR=''
)
GSPARAMS.update([(k, os.getenv(k)) for k in GSPARAMS if k in os.environ])

DBPARAMS = dict(
    host=os.getenv("DBHOST", "localhost"),
    port=os.getenv("DBPORT", "5432"),
    dbtype=os.getenv("DBTYPE", "postgis"),
    database=os.getenv("DATABASE", "db"),
    user=os.getenv("DBUSER", "postgres"),
    passwd=os.getenv("DBPASS", "password")
)
print '*** GSPARAMS ***'
print GSPARAMS
print '*** DBPARAMS ***'
print DBPARAMS
print '****************'
