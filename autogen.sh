#!/bin/sh
# Run this to generate all the initial makefiles, etc.

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

ORIGDIR=`pwd`
cd $srcdir
PROJECT=pygtkglext
TEST_TYPE=-f
FILE=gtk/gdkgl/gdkglext-types.defs

DIE=0

test -z "$AUTOCONF" && AUTOCONF=autoconf
test -z "$AUTOHEADER" && AUTOHEADER=autoheader

(autoconf --version) < /dev/null > /dev/null 2>&1 || {
	echo
	echo "You must have autoconf installed to compile $PROJECT."
	echo "Download the appropriate package for your distribution,"
	echo "or get the source tarball at ftp://ftp.gnu.org/pub/gnu/"
	DIE=1
}

(libtool --version) < /dev/null > /dev/null 2>&1 || {
        echo
        echo "You must have libtool installed to compile $PROJECT."
        echo "Get ftp://ftp.gnu.org/gnu/libtool/libtool-1.4.tar.gz"
        echo "(or a newer version if it is available)"
        DIE=1
}

if test -z "$AUTOMAKE"; then
  if automake-1.7 --version < /dev/null > /dev/null 2>&1; then
    AUTOMAKE=automake-1.7
    ACLOCAL=aclocal-1.7
  elif automake-1.6 --version < /dev/null > /dev/null 2>&1; then
    AUTOMAKE=automake-1.6
    ACLOCAL=aclocal-1.6
  else
    echo
    echo "You must have automake installed to compile $PROJECT."
    echo "Get ftp://ftp.gnu.org/pub/gnu/automake/automake-1.7.2.tar.gz"
    echo "(or a newer version if it is available)"
    DIE=1
  fi
fi

if test "$DIE" -eq 1; then
	exit 1
fi

test $TEST_TYPE $FILE || {
	echo "You must run this script in the top-level $PROJECT directory"
	exit 1
}

if test -z "$*"; then
	echo "I am going to run ./configure with no arguments - if you wish "
        echo "to pass any to it, please specify them on the $0 command line."
fi

case $CC in
*xlc | *xlc\ * | *lcc | *lcc\ *) am_opt=--include-deps;;
esac

if test -z "$ACLOCAL_FLAGS"; then

	acdir=`$ACLOCAL --print-ac-dir`
        m4list="glib-2.0.m4 gtk-2.0.m4 gettext.m4"

	for file in $m4list
	do
		if [ ! -f "$acdir/$file" ]; then
			echo "WARNING: aclocal's directory is $acdir, but..."
			echo "         no file $acdir/$file"
			echo "         You may see fatal macro warnings below."
			echo "         If these files are installed in /some/dir, set the ACLOCAL_FLAGS "
			echo "         environment variable to \"-I /some/dir\", or install"
			echo "         $acdir/$file."
			echo ""
		fi
	done
fi

#echo "Running gettextize...  Ignore non-fatal messages."
# Hmm, we specify --force here, since otherwise things dont'
# get added reliably, but we don't want to overwrite intl
# while making dist.
#echo "no" | gettextize --copy --force

$ACLOCAL $ACLOCAL_FLAGS

# optionally feature autoheader
($AUTOHEADER --version)  < /dev/null > /dev/null 2>&1 && $AUTOHEADER

# run libtoolize ...
libtoolize --force

$AUTOMAKE -a $am_opt
$AUTOHEADER
$AUTOCONF
cd $ORIGDIR

$srcdir/configure --enable-maintainer-mode "$@"

echo 
echo "Now type 'make' to compile $PROJECT."
