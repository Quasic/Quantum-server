#!/usr/bin/perl
#
# Quantum Gaming Server, Quintrix and Crew Software
#
# Released as Creative Commons BY-NC, where 
# 'non-commercial' includes games created meaning
# games cannot have money, coins, bank notes,
# credits, or any other economic system.
#
# See license.txt for full credits and details.
#
# http://creativecommons.org/licenses/by-nc/2.0/
#
 
use CGI::Carp qw( fatalsToBrowser );
$| = -1;

$sstatus="On";

$datadir="/home/quin/q";
$htmldir="/home/quin/q/public_html";
$htmlurl="http://quintrixandcrew.com";
$gfxurl="http://quintrixandcrew.com/11-gfx";

$cstamp=time(); $timestamp=sprintf("%08x", $cstamp); srand();

print "Content-type: text/html\n";
print "Cache-Control: no-cache, no-store, must-revalidate\n";
print "Expires: Fri, 30 Oct 1998 14:19:41 GMT\n";
print "Access-Control-Allow-Origin: *\n";
print "Access-Control-Allow-Methods: POST, GET\n";
print "Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept\n";
print "Pragma: no-cache\n\n";
if ($sstatus eq "Off") { print "pop=server has been turned off\n"; exit; }
if ($ENV{"REQUEST_METHOD"} eq 'GET') { $buffer = $ENV{'QUERY_STRING'}; } else { read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); }
@pairs = split(/&/, $buffer); foreach $pair (@pairs) {
 ($name,$value)=split(/=/,$pair);
 $value =~ tr/+/ /; $value =~ s/%39/=/; $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
 $form{$name} = $value; #print qq~document.write("$name = $value<br>");\n ~;
}

## $form = (n)ame (p)swd (s)erver (c)ommand (d)ata

$form{'s'}=~s/[^A-Za-z0-9\-]//g;
$form{'c'}=~s/[^A-Za-z0-9\-]//g;
$form{'d'}=~s/[^A-Za-z0-9 \-]//g;

$error="";

$server=lc($form{'s'});
if (length($server)>16) {}

if (!$server) {
 ## if no server provided, send client as response 
 open (FILE, "client-itemid.js"); @itemid=<FILE>; close FILE;
 open (FILE, "client.htm"); @client=<FILE>; close FILE;
 foreach $line (@client) {
  chomp($line);
  $line =~ s/\[htmlurl\]/$htmlurl/gi;
  $line =~ s/\[itemid\]/@itemid/gi;
  print "$line\n";
 }
 exit;
}

#
# if url has .js in it, return javascript client
#

$name=$form{'n'}; $name=lc($name); $name=~s/[^a-z0-9]//g;

if (-e "$datadir/p/$name.txt") {
  if ($form{'c'} eq "log") {
    if ($form{'d'} eq $form{'p'}) {
      print "error=player file already exists\n";
    }
  } else {
    open (FILE,"$datadir/p/$name.txt");
    chomp ($pass=<FILE>);
    close FILE;
    if ($pass ne $form{'p'}) { print "error=Password mismatch\n"; }
  }
} else {
  if ($form{'d'} eq $form{'p'}) {
    if ($name ne $form{'n'}) { $error.="Invalid Character In Name\n"; }
    if (length($name)<3) { $error.="Name must be at least 3 characters\n"; }
    #if (length($name)>16) { $error.="Name cannot be more than 16 characters\n"; }
    $filename=lc($name);
    if (substr($name,0,1) lt "a" || substr($filename,0,1) gt "z") { $error.="Name must start with a letter\n"; }
    #if (substr($name,0,3) eq "npc") {  $error.="Restricted player name (npc)\n"; }
    #validate password here
    if ($pass ne $form{'p'}) { $error.="Invalid character in password\n"; }
    if (length($pass)<4) { $error.="Password must be at least 4 characters\n"; }
    if (length($pass)>32) { $pswd=substr($pswd,0,32); }
    #
    mkdir ("$datadir/$name");
    open (FILE,">$datadir/p/$name.txt");
    print FILE "$form{'p'}";
    close FILE;
    print "pop=player file created\n";
  } else {  
    print "error=Player file does not exist\n";
  }
}

if ($server eq "" or $server eq 'l') {
  ## display list of servers - can use dragon.htm as client for this purpose
  #open dir, send s= for each subdir except 11-dragon
  opendir(DIR,$datadir);
  while($s=readdir(DIR)){print "s=$s\n" if substr($s,0,1)ne'.'&&$s ne 'p';}
  closedir(DIR);
  print "servers=\n";
  exit;
}

$datadir.="/$server";

if (-e "$datadir") {
  #
  # read directory
  # send list of items
  # send list of expired
  #
  # execute command:
  #  -get [start z]-[end z]
  #  -lod [loads objects]
  #  -obj [item][object]
  #  -add [item][z][exp]
  #  -del [item][z]
  #  -mov [item][z][new-z]
  #  -ren [item][z][new-item]
  #   exp [item][z][new-expires]
  #
  # things to do:
  #  check list of expired items, if player token logout
  #
  
  if ($form{'c'} eq "lod") {
    opendir(DIR,"$datadir/"); @data=readdir(DIR); closedir(DIR);
    foreach $rec (@data) {
      chomp($rec); $rec=~s/.txt//g; if (length($rec)<3) { next; }
      ($item,$z,$exp)=split(/-/, $rec);
      if ($item=~/W/) {
        open (FILE, "$datadir/$item-$z-$exp.txt"); $obj=<FILE>; close FILE; chomp($obj);
        print "o=$item-$obj\n";
        #print "alert=$item-$obj\n";
      }
    }
    print "start=";
  }
    
  if ($form{'c'} eq "get") {
    opendir(DIR,"$datadir/"); @data=readdir(DIR); closedir(DIR);
    $objfile=0; $i=""; $e=""; foreach $rec (@data) {
      chomp($rec); $rec=~s/.txt//g; if (length($rec)<3) { next; }
      ($item,$z,$exp)=split(/-/, $rec);
      #print "pop=$item $z $exp\n";
      if ($exp ne "0000000000") { 
        if ($cstamp>$exp) {
          print "pop=$item expired $exp\n";
          unlink ("$datadir/$rec.txt");
          $e.="$item$z";
          if ($item=~/W/) { $objfile=1; }
        } else {
          $i.="$item$z";
        }
      } else {
        $i.="$item$z";
      }
    }
    print "items=$i\n";
    print "eitem=$e\n";
  }

  if ($form{'c'} eq "ply") {
    ($obj,$z,$exp)=split(/-/,$form{'d'});
    $obj=~s/[^A-Za-z0-9]//g; $z=~s/[^A-Za-z0-9]//g; $exp=~s/[^0-9]//g;
    while (length($z)<3) { $z="0".$z; } if (length($z)==3) {} else { $z="078"; }
    
    if (length($z)==3) {
      $exp=$cstamp+$exp;
      $item="";

      opendir(DIR,"$datadir");
      @data=readdir(DIR);
      closedir(DIR);

      #get list of player tokens in-game
      $item=""; $i=""; foreach $rec (@data) {
        chomp($rec); $rec=~s/.txt//g; 
        if (length($rec)<3) { next; }
        ($item,$a,$b)=split(/-/, $rec);
        if ($item=~/W/) { $i.="$item"; }
      }

      for $f ('a' .. 'z') {
        if ($i=~/W$f/) { next; } else {
          $item="W$f"; open (FILE, ">$datadir/$item-$z-$exp.txt");
          print FILE "$obj"; close FILE; print "token=$item\n"; last;
        }
      } 
      print "pop=Player Added\n";
      print "start=\n";      
    } else {
      print "pop=bad z\n";
    }
    if ($item eq "") {
      print "err=Server Full\n";
    }
  }

  if ($form{'c'} eq "add") { 
    ($item,$z,$exp)=split(/-/,$form{'d'});
    $item=~s/[^A-Za-z0-9]//g; $z=~s/[^A-Za-z0-9]//g; $exp=~s/[^0-9]//g;
    while (length($z)<3) { $z="0".$z; }
    if (length($z)==3) {
      if (glob "$datadir/$item-$z-??????????.txt") {
        #print "pop=item exists\n";
      } else {
        if ($exp) { $exp=$cstamp+$exp; } else { $exp="0000000000"; }
        open (FILE, ">$datadir/$item-$z-$exp.txt"); print FILE ""; close FILE;
        #print "pop=$item added\n";
      }   
    } else {
      print "pop=bad z\n";
    }
  }

  if ($form{'c'} eq "del") {
    $f=0; ($item,$obj)=split(/-/,$form{'d'});
    $obj=~s/[^A-Za-z0-9]//g; $item=~s/[^A-Za-z0-9]//g;
    if (length($item)==5) {
      $itemz=substr($item,2,length($item));
      $item=substr($item,0,2);
      while (length($itemz)<3) { $itemz="0".$itemz; }
      $a=glob "$datadir/$item-$itemz-??????????.txt";
      if ($a) {
        $b=substr($a,length($a)-14,10);
        unlink ("$datadir/$item-$itemz-$b.txt");
        print "pop=$item Deleted\n";        
      } 
    }
  }

  if ($form{'c'} eq "obj") {
    $f=0; ($item,$obj)=split(/-/,$form{'d'});
    $obj=~s/[^A-Za-z0-9]//g; $item=~s/[^A-Za-z0-9]//g;
    if (length($item)==5) {
      $itemz=substr($item,2,length($item));
      $item=substr($item,0,2);
      while (length($itemz)<3) { $itemz="0".$itemz; }
      $a=glob "$datadir/$item-$itemz-??????????.txt";
      if ($a) {
        $b=substr($a,length($a)-14,10);
        open (FILE, ">$datadir/$item-$itemz-$b.txt");
        print FILE "$obj"; 
        close FILE;
        print "pop=$item set to $obj\n";        
      } 
    }
  }

  if ($form{'c'} eq "ren") {
    $f=0; ($item,$obj)=split(/-/,$form{'d'});
    $obj=~s/[^A-Za-z0-9]//g; $item=~s/[^A-Za-z0-9]//g;

    if (length($item)>2 && length($item)<6) {
      $itemz=substr($item,2,length($item));
      $item=substr($item,0,2);

      while (length($itemz)<3) { $itemz="0".$itemz; }
      $a=glob "$datadir/$item-$itemz-??????????.txt";
  
      if ($a) {
        if (length($obj)==2) {
          $b=substr($a,length($a)-14,10);
          rename ("$datadir/$item-$itemz-$b.txt", "$datadir/$obj-$itemz-$b.txt");
          print "pop=$item Renamed\n";
        }
      }        
    } 
  }

  if ($form{'c'} eq "mov") {
    ($item,$z)=split(/-/,$form{d});
    $item=~s/[^A-Za-z0-9]//g;
    $z=~s/[^A-Za-z0-9]//g;
    while (length($z)<3) { $z="0".$z; }
    if (length($z)==3) {
      if (length($item)>2) {
        $itemz=substr($item,2,length($item));
        $item=substr($item,0,2);
        while (length($itemz)<3) { $itemz="0".$itemz; }
        $a=glob "$datadir/$item-$itemz-??????????.txt";
        $b=substr($a,length($a)-14,10); 
        rename ("$datadir/$item-$itemz-$b.txt", "$datadir/$item-$z-$b.txt");        
      }
    }
  }
  
} else {
  ## server does not exist
  print"error=Server does not exist\n";
  exit;
}

if ($error) {
  print "error=$error";
}
