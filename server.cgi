#!/usr/bin/perl

# Quantum Gaming Server, Quintrix and Crew Software
# Released as Creative Commons BY-NC, where 'non-commercial'
# includes games created meaning games cannot have money, coins,
# bank notes, credits, or any other economic system.
# See license.txt for full credits and details.
# http://creativecommons.org/licenses/by-nc/2.0/
 
use CGI::Carp qw( fatalsToBrowser );
$| = -1;
$sstatus="On";
$datadir="/home/quin/q";
$htmldir="/home/quin/q/public_html";
$htmlurl="http://quintrixandcrew.com";
$gfxurl="http://quintrixandcrew.com/11-gfx";
$cstamp=time(); $timestamp=sprintf("%08x", $cstamp); srand();

print qq~Content-type: text/html
Cache-Control: no-cache, no-store, must-revalidate
Expires: Fri, 30 Oct 1998 14:19:41 GMT
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: POST, GET
Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept
X-Content-Type-Options: nosniff
Pragma: no-cache

~;
if ($sstatus eq "Off") { print "pop=server has been turned off\n"; exit; }
if ($ENV{"REQUEST_METHOD"} eq 'GET') { $buffer = $ENV{'QUERY_STRING'}; } else { read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); }
@pairs = split(/&/, $buffer); foreach $pair (@pairs) { ($name,$value)=split(/=/,$pair); $value=~tr/+/ /; $value=~s/%39/=/; $value=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg; $form{$name}=$value; }
## $form = (n)ame (p)swd (s)erver (c)ommand (d)ata
$form{'s'}=~s/[^A-Za-z0-9\-]//g; $form{'c'}=~s/[^A-Za-z0-9\-]//g; $form{'d'}=~s/[^A-Za-z0-9 \-]//g;
$error=""; $server=lc($form{'s'}); if (length($server)>16) {}
if (!$server) { open (FILE, "client-itemid.js"); @itemid=<FILE>; close FILE; open (FILE, "client.htm"); @client=<FILE>; close FILE; foreach $line (@client) { $line =~ s/\[htmlurl\]/$htmlurl/gi; $line =~ s/\[itemid\]/@itemid/gi; print "$line"; } exit; }
$name=$form{'n'}; $name=lc($name); $name=~s/[^a-z0-9]//g;
if ($server eq "" or $server eq 'l') { opendir(DIR,$datadir); while($s=readdir(DIR)){ chomp($s); $s=~s/.txt//g; if (length($s)<3) { next; } print "s=$s\n"; } closedir(DIR); print "servers=\n"; exit; }
if (!-e "$datadir/$server") {
 if (length($server)==2) {
  $form{'s'}=~s/[^a-z0-9]//g; if (substr($server,0,1) lt "a" || substr($server,0,1) gt "z") { $server=""; print "pop=Map must start with letter\n"; } else {
  if (!-d "$datadir/$server") { mkdir "$datadir/$server" }
  if (!-w "$datadir$server") { chmod 0777, "$datadir/$server" }  
  open (FILE,">$datadir/$server/m.txt"); print FILE "GaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGa"; close FILE; }
 } else {
   ## validate 'player map' (sysop? create directory, generate random map)
   $form{'s'}=~s/[^a-z0-9]//g;
   if (substr($server,0,1) lt "a" || substr($server,0,1) gt "z") { 
     $server=""; print "pop=Map must start with letter\n";
   } else {
     if (length($server)>16) {
       $server=""; print "pop=Map must be less than sixteen characters\n";
     } else {
       if (!-d "$datadir/$server") { mkdir "$datadir/$server"; }
       if (!-w "$datadir$server") { chmod 0777, "$datadir/$server"; }  
       open (FILE,">$datadir/$server/m.txt"); print FILE "GaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGaGa"; close FILE;
     }
   }
 }
}

if ($server) { $datadir.="/$server"; } else { print "error=invalid server\n"; }
if (-e "$datadir") {
 # read directory, send list of items, execute command:
 #   -get [start z]-[end z]
 #   -lod [loads objects]
 #   -obj [item][object]
 #   -add [item][z][exp]
 #   -del [item][z]
 #   -mov [item][z][new-z]
 #   -ren [item][z][new-item]
 #  k-bld [name or item]-[data]
 #  k-ext [north]-[south]-[east]-[west]-[building or z-location or zero for scrolling]
 #  k-map [map][tileset]
 #    exp [item][z][new-expires]
 if ($form{'c'} eq "get") {
  opendir(DIR,"$datadir/"); @data=readdir(DIR); closedir(DIR);
  $i=""; $d=""; $e=$cstamp+60; foreach $rec (@data) {
   chomp($rec); $rec=~s/.txt//g; if (length($rec)<3) { next; }
   ($item,$z,$exp)=split(/-/, $rec);
   #print "pop=$item $z $exp\n";
   if ($exp ne "0000000000") { if ($cstamp>$exp) { unlink ("$datadir/$rec.txt");
    ## expiration engine here
    if ($item=~/Ia/) { $d=rand(); if ($d>.8) { $d="Fd"; } else { if ($d>.6) { $d="Fc"; } else { if ($d>.4) { $d="Fb"; } else { if ($d>.2) { $d="Fa"; } else { $d=""; }}}}}
    if ($d) { $i.="$d$z"; open (FILE, ">$datadir/$d-$z-$e.txt"); print FILE "$obj"; close FILE; }
   } else { $i.="$item$z"; }} else { $i.="$item$z"; }
  }
  print "items=$i\n"; exit;
 }
 if ($form{'c'} eq "mov") {
  ($item,$z)=split(/-/,$form{d}); $item=~s/[^A-Za-z0-9]//g; $z=~s/[^A-Za-z0-9]//g; while (length($z)<2) { $z="0".$z; }
  if (length($z)==2) { if (length($item)>2) {
   $itemz=substr($item,2,length($item)); $item=substr($item,0,2); while (length($itemz)<2) { $itemz="0".$itemz; }
   $a=glob "$datadir/$item-$itemz-??????????.txt"; $b=substr($a,length($a)-14,10); $e=$cstamp+60; if (-e "$datadir/$item-$itemz-$b.txt") { rename ("$datadir/$item-$itemz-$b.txt", "$datadir/$item-$z-$e.txt"); } else { print "token=\n"; }        
  }} exit;
 }
 if ($form{'c'} eq "lod") {
  opendir(DIR,"$datadir/"); @data=readdir(DIR); closedir(DIR); foreach $rec (@data) {
   chomp($rec); $rec=~s/.txt//g; if (length($rec)<3) { next; } ($item,$z,$exp)=split(/-/, $rec);
   if ($item=~/V/) { open (FILE, "$datadir/$item-$z-$exp.txt"); chomp($obj=<FILE>); close FILE; print "o=$item-$obj\n"; }
   if ($item=~/W/) { open (FILE, "$datadir/$item-$z-$exp.txt"); chomp($obj=<FILE>); close FILE; print "o=$item-$obj\n"; }
  }
  if (-e "$datadir/m.txt") { open (FILE, "$datadir/m.txt"); chomp ($map=<FILE>); close FILE; print "map=$map\n"; } 
  if (-e "$datadir/x.txt") { open (FILE, "$datadir/x.txt"); chomp ($exit=<FILE>); close FILE; print "exit=$exit\n"; }
  print "start="; exit;
 }
 if ($form{'c'} eq "ply") {
  ($obj,$z,$exp)=split(/-/,$form{'d'});
  $obj=~s/[^A-Za-z0-9]//g; $z=~s/[^A-Za-z0-9]//g; $exp=~s/[^0-9]//g;
  while (length($z)<2) { $z="0".$z; } if (length($z)==2) {} else { $z="3e"; }
  if (length($z)==2) {
   $exp=$cstamp+$exp; $item=""; opendir(DIR,"$datadir"); @data=readdir(DIR); closedir(DIR); $item=""; $i=""; foreach $rec (@data) {
   chomp($rec); $rec=~s/.txt//g; if (length($rec)<3) { next; } ($item,$a,$b)=split(/-/, $rec); if ($item=~/W/) { $i.="$item"; }
  }
  $g=0; for $f ('a' .. 'z') { if ($i=~/W$f/) { next; } else { $g=1; $item="W$f"; open (FILE, ">$datadir/$item-$z-$exp.txt"); print FILE "$obj"; close FILE; print "token=$item\n"; last; }} 
  if ($g) { print "start=\n"; } else {
   ## check files for expiration here somehow
   print "pop=Server Full\n";
  }} else { print "pop=bad z\n"; }
  if ($item eq "") { print "err=Server Full\n"; } exit;
 }
  if ($form{'c'} eq "add") { 
   ($item,$z,$exp)=split(/-/,$form{'d'}); $item=~s/[^A-Za-z0-9]//g; $z=~s/[^A-Za-z0-9]//g; $exp=~s/[^0-9]//g; while (length($z)<2) { $z="0".$z; }
   if (length($z)==2) {
    if (glob "$datadir/[!W]?-$z-??????????.txt") {
    #print "pop=item exists\n";
   } else { if ($exp) { $exp=$cstamp+$exp; } else { $exp="0000000000"; } open (FILE, ">$datadir/$item-$z-$exp.txt"); print FILE ""; close FILE; }} exit;
 }
 if ($form{'c'} eq "del") {
  $f=0; ($item,$obj)=split(/-/,$form{'d'}); $obj=~s/[^A-Za-z0-9]//g; $item=~s/[^A-Za-z0-9]//g;
  if (length($item)==4) { $itemz=substr($item,2,length($item)); $item=substr($item,0,2); while (length($itemz)<2) { $itemz="0".$itemz; } $a=glob "$datadir/$item-$itemz-??????????.txt"; if ($a) { $b=substr($a,length($a)-14,10); unlink ("$datadir/$item-$itemz-$b.txt"); }} exit;
 }

 if ($form{'c'} eq "obj") {
  $f=0; ($item,$obj)=split(/-/,$form{'d'}); $obj=~s/[^A-Za-z0-9]//g; $item=~s/[^A-Za-z0-9]//g;
  if (length($item)==4) {
   $itemz=substr($item,2,length($item)); $item=substr($item,0,2); while (length($itemz)<2) { $itemz="0".$itemz; }
   $a=glob "$datadir/$item-$itemz-??????????.txt"; if ($a) { $b=substr($a,length($a)-14,10); open (FILE, ">$datadir/$item-$itemz-$b.txt"); print FILE "$obj"; close FILE; } 
  }
  exit;
 }

 if ($form{'c'} eq "ren") {
  $f=0; ($item,$obj)=split(/-/,$form{'d'}); $obj=~s/[^A-Za-z0-9]//g; $item=~s/[^A-Za-z0-9]//g;
  if (length($item)>2 && length($item)<6) {
   $itemz=substr($item,2,length($item)); $item=substr($item,0,2); while (length($itemz)<2) { $itemz="0".$itemz; }
   $a=glob "$datadir/$item-$itemz-??????????.txt"; if ($a) { if (length($obj)==2) { $b=substr($a,length($a)-14,10); rename ("$datadir/$item-$itemz-$b.txt", "$datadir/$obj-$itemz-$b.txt"); }}        
  }
  exit; 
 }

 if ($form{'c'} eq "bld") {
  ($obj,$dat,$z)=split(/-/,$form{d});
  $obj=~s/[^A-Za-z0-9]//g; $dat=~s/[^A-Za-z0-9]//g; $z=~s/[^A-Za-z0-9]//g;
  if (!$z) { $z=$dat; $dat=""; } while (length($z)<2) { $z="0".$z; }
  if (length($z)==2) { 
   if (length($obj)>1) {
    $i=""; $item=""; opendir(DIR,"$datadir"); @data=readdir(DIR); closedir(DIR);
    foreach $rec (@data) {
     chomp($rec); $rec=~s/.txt//g; if (length($rec)<3) { next; }
     ($item,$a,$b)=split(/-/, $rec); if ($item=~/V/) { $i.="$item"; }
    }
    for $f ('a' .. 'z') { 
     if ($i=~/V$f/) { next; } else {
      $item="V$f"; print "pop=$item $obj-$dat\n";
      open (FILE, ">$datadir/$item-$z-0000000000.txt"); print FILE "$obj-$dat"; close FILE;
      last;
     }
    }
   }
  }
  exit;
 }
    
 if ($form{'c'} eq "map") {
   # password check?? 
   # if any client can edit maps, clients can alter landscape
   # like growing weeds and deterating paths that players must
   # fix - if only sysop can edit maps, then maps become more
   # static ... perhaps a locking key system?? creates problems
   $form{'d'}=~s/[^A-Za-z0-9]//g; if ($form{d}) { open (FILE, ">$datadir/m.txt"); print FILE "$form{d}"; close FILE; print "pop=Map Saved\n"; }
 }
 if ($form{'c'} eq "ext") { if ($form{'d'}) { open (FILE, ">$datadir/x.txt"); print FILE "$form{'d'}"; close FILE; print "pop=Exits Saved\n"; } }
 exit;
}

if ($error) { print "error=$error"; }
