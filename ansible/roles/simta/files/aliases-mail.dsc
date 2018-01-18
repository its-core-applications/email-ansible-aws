# Alias file for mail.dsc.umich.edu
# Based on modified standard alias file from pigeon

# Basic system aliases -- these MUST be present.

mailer-daemon:postmaster
postmaster:postmast@hawkgirl.dsc.umich.edu

# Aliases to handle mail to msgs and news

nobody: /dev/null

# General redirections for pseudo accounts. Merges default Linux,
# default AIX, and some general UM ids. Sorted.

1migrate:	root
abuse:		root
adm:		root
amanda:		root
apache:		nobody
avahi-autoipd:	root
avahi:		root
bin:		root
canna:		root
daemon:		root
dbus:		root
desktop:	root
distcache:	root
dovecot:	root
dumper:		root
fax:		root
ftp-adm:	ftp
ftp-admin:	ftp
ftp:		root
ftpadm:		ftp
ftpadmin:	ftp
games:		root
gdm:		root
gopher:		root
haldaemon:	root
halt:		root
hostmaster:	root
ident:		root
info:		postmaster
ingres:		root
ldap:		root
lp:		root
mail:		root
mailnull:	root
manager:	root
marketing:	postmaster
named:		root
netdump:	root
news:		root
newsadm:	news
newsadmin:	news
nfsnobody:	root
noc:		root
nscd:		root
ntp:		root
nut:		root
operator:	root
pcap:		root
postfix:	root
postgres:	root
privoxy:	root
pvm:		root
quagga:		root
radiusd:	root
radvd:		root
rpc:		root
rpcuser:	root
rpm:		root
sales:		postmaster
security:	root
shutdown:	root
smmsp:		root
squid:		root
sshd:		root
support:	postmaster
sync:		root
system:		root
toor:		root
usenet:		news
uucp:		root
vcsa:		root
webalizer:	root
webmaster:	root
wnn:		root
www:		webmaster
xfs:		root

# mailman aliases

mailman:	postmaster
mailman-owner:	postmaster

# Trap decode to catch security attacks

decode:		root

# Alias for root

root:unix_admins
owner-root:dnowell

# Alias for Unix Sys admins to tell them about all those nifty reports

unix_admins:its.system.support.unix.root@umich.edu
owner-unix_admins:dnowell

# Alias for the daily reports -- full text

dailyrpt:unix_admins
owner-dailyrpt:dnowell

# Alias for the 'rc.dropkick' report

dropkick:unix_admins,
         dianekl,
         barbins,
         aleec
owner-dropkick:dnowell

# Alias for mcreat1 on gateway servers
mcreat1:mc-webops@umich.edu


# Alias for the daily reports -- short text (check_nodes)

checkrpt:unix_admins,
         aleec,
         barbins,
         bjanice,
         cmkorsal,
         dianekl,
         ganglu,
         gtessmer,
         cmkorsal,
         tmsaxon
owner-checkrpt:dnowell

# Alias for Adsm tape reports

adsmrpt:lisalee,
        aleec,
        barbins,
        bjanice,
        cmkorsal,
        dianekl,
        ganglu,
        gtessmer,
        cmkorsal,
        tmsaxon
owner-adsmrpt:lisalee

# Various accounts that generate system reports

1bmcfdtd:root
owner-1bmcfdtd:root

# From legacy hoopoe, may be no longer needed.  scs, 2012/11/28

1dscpln:farrellj
owner-1dscpln:root
1dscpln2:farrellj
owner-1dscpln2:root
1webstat:farrellj
owner-1webstat:root

# Alias for Adsm Citrix backup reports

adsmrpt_nt:mais.tio.wes@umich.edu,
           bobh,
           lisalee
owner-adsmrpt_nt:lisalee

# General peoplesoft (psoft) mail

psoft:its.is.csi.awi@umich.edu
owner-psoft:root

# Alias for the Peoplesoft folks that wil get notified
# when a "ftp-psoft-reports" does not complete -- or
# leaves the status file laying around.

ftp_psoft:billw,
          thouser
owner-ftp_psoft:psoft

# Alias for monthly disk use report

diskrpt:unix_admins,
        rdake
owner-diskrpt:dnowell

# Alias for backup notifications

notify:unix_admins,
       lisalee,
       dsc.oradba@umich.edu
owner-notify:dnowell

# Alias for the daily reports -- full text

cookie_crumbs:unix_admins,
         kkit,
         tngo,
         mhaskins
owner-cookie_crumbs:dnowell

dnowell_ess:dnowell

# Alias for various SSA related warnings

ssa_adm:root
owner-ssa_adm:dnowell

# Alias for Storage

sanadmin:its.enterprise.storage@umich.edu
its.enterprise.storage:its.enterprise.storage@umich.edu
owner-its.enterprise.storage:dnowell

# Aliases for Oracle database accounts. As more accounts are
# added, unless otherwise specified they should be set to simple
# 'oracle', not to the @umich.edu version.

oracle:its.is.oradba@umich.edu
owner-oracle:root
9pinncus:oracle
owner-9pinncus:root

# Aliases for mysql database accounts. As more accounts are
# added, unless otherwise specified they should be set to simple
# 'mysql', not to the @umich.edu version.

mysql:its.is.mysql.dba@umich.edu
owner-mysql:root

# Aliases for U-M Web Gateway
umweb:umweb.machine.messages@umich.edu

# Alias for SSV

ssv_team:dnowell,
         nmedd,
         scs,
         lisalee,
         pjessel
owner-ssv_team:dnowell

# Mcommunity and friends

mcommadm:iamopsmon@umich.edu
owner-mcommadm:root
umiac:iamopsmon@umich.edu
owner-umiac:root

# Ctools and friends

ctools:watsopmon@umich.edu
owner-ctools:root
ctadmin:watsopmon@umich.edu
owner-ctadmin:root

# The splunk crew

splunk:its.splunk.admins@umich.edu
owner-splunk:root

# End-user computing print services
papercut:euc.print@umich.edu
owner-papercut:root
miprint1:euc.print@umich.edu
owner-miprint1:root

# EDI
ediadm:its.is.csi.awi@umich.edu
owner-ediadm:root
etl1:its.is.csi.awi@umich.edu
owner-etl1:root

# CA-Unicenter

ca7mngr:root
owner-ca7mngr:root

# Dazel

dazel:its.is.csi.awi@umich.edu
owner-dazel:root

# service-now

7smemail: umichdev@service-now.com
7smpdail: umichprod@service-now.com
7smqaail: umichqa@service-now.com

# Active user personal accounts
#
# Active user aliases. These are people who have personal accounts
# and run crontabs, have mail generated directly to them, or
# have an alias that points a service at them. Some of these may
# be obsolete, but until proven otherwise (and someone steps into
# the role) we'll forward their mail to their umich account.

aleec:aleec@umich.edu
amlevitt:amlevitt@umich.edu
armadden:armadden@umich.edu
azur:azur@umich.edu
barbins:barbins@umich.edu
bawood:bawood@umich.edu
beckytho:beckytho@umich.edu
billw:billw@umich.edu
bjanice:bjanice@umich.edu
bkirschn:bkirschn@umich.edu
bmcrae:bmcrae@umich.edu
bobh:bobh@umich.edu
brucetim:brucetim@umich.edu
bwitten:bwitten@umich.edu
cdacko:cdacko@umich.edu
cengle:cengle@umich.edu
chanover:chanover@umich.edu
cmkorsal:cmkorsal@umich.edu
colinj:colinj@umich.edu
cousinea:cousinea@umich.edu
cwood:cwood@umich.edu
davemc:davemc@umich.edu
ddsulliv:ddsulliv@umich.edu
deliac:deliac@umich.edu
dianekl:dianekl@umich.edu
djneil:djneil@umich.edu
dnowell:dnowell@umich.edu
edie:edie@umich.edu
farrellj:farrellj@umich.edu
ganglu:ganglu@umich.edu
gnystrom:gnystrom@umich.edu
goffn:goffn@umich.edu
gtessmer:gtessmer@umich.edu
jalpa:jalpa@umich.edu
jaynair:jaynair@umich.edu
jbouffor:jbouffor@umich.edu
jbujaki:jbujaki@umich.edu
jfoster:jfoster@umich.edu
jmfeaton:jmfeaton@umich.edu
josman:josman@umich.edu
jprzyby:jprzyby@umich.edu
jsmutek:jsmutek@umich.edu
jwcharle:jwcharle@umich.edu
kasthuri:kasthuri@umich.edu
kbansal:kbansal@umich.edu
khillig:khillig@umich.edu
kkit:kkit@umich.edu
kriscarl:kriscarl@umich.edu
kstam:kstam@umich.edu
lbater:lbater@umich.edu
liamr:liamr@umich.edu
linlan:linlan@umich.edu
lisalee:lisalee@umich.edu
lrfoley:lrfoley@umich.edu
ltracy:ltracy@umich.edu
lubomirs:lubomirs@umich.edu
mafaith:mafaith@umich.edu
makhmoor:makhmoor@umich.edu
mattbing:mattbing@umich.edu
mbumby:mbumby@umich.edu
mdw:mdw@umich.edu
mhaskins:mhaskins@umich.edu
mmmonfor:mmmonfor@umich.edu
myrt:myrt@umich.edu
ncharles:ncharles@umich.edu
neda:neda@umich.edu
neener:neener@umich.edu
nmedd:nmedd@umich.edu
pjessel:pjessel@umich.edu
pkkumar:pkkumar@umich.edu
qszhu:qszhu@umich.edu
rdake:rdake@umich.edu
reba:reba@umich.edu
redi:redi@umich.edu
rgrussel:rgrussel@umich.edu
rharolde:rharolde@umich.edu
rkcarter:rkcarter@umich.edu
scs:scs@umich.edu
ssmaynar:ssmaynar@umich.edu
stembrit:stembrit@umich.edu
tchapin:tchapin@umich.edu
thouser:thouser@umich.edu
tngo:tngo@umich.edu
tmsaxon:tmsaxon@umich.edu
vicky:vicky@umich.edu
vpliakas:vpliakas@umich.edu
xueyan:xueyan@umich.edu
