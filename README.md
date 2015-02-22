##PYSOS 

Pysos is a python utility to quickly parse through a sosreport and present relevant information quickly and in a more digestible format than reading the raw data.

###Installation

Installation is simple, clone this git repo and then drop a symlink somewhere in your $PATH. A proper `setup.py` installation method is in the works.

    $ git clone https://github.com/turboturtle/pysos
    $ ln -s $somedir/pysos.py /usr/local/bin/pysos


###Usage

Pysos takes any number of the following arguments followed by the target directory, i.e. the top level of the sosreport directory:

    positional arguments:
	  target                Target directory, aka the sosreport root.

	optional arguments:
      -h, --help            show this help message and exit
      -a, --getall          Print all information (RHEV excluded)
      -b, --bios            Print BIOS and dmidecode information
      -o, --os              Print OS information
      -k, --kdump, --kernel
                            Print kdump and kernel information
      -c, --cpu             Print CPU information ONLY
      -m, --memory          Print memory information
      -d, --disk            Print block device and multipath information
      -f, --filesys         Print filesystem information
      --fso                 Print filesystem information AND mount options
      -l, --lspci           Print lspci information
      -e, --ethtool         Print ethtool information
      -g, --bonding         Print bonding information
      -i, --ip              Print IP information
      -n, --netdev          Print proc/net/dev information
      --net                 Alias for --ethtool, --bonding, --ip, --netdev
      --vnet                Also display vnet interfaces in network output
      -s, --sysctl          Print common sysctl settings
      -p, --ps              Print process information
      -r, --rhev            Print RHEV information
      --db                  Print RHEV DB information
      -v, --virt            Print KVM Virtualization information
      -y, --yum             Print yum/RHN information


###Requirements

Pysos is written for Python 2.7 and with the exception of the `argparse` module requires nothing outside the standard library to function.


###Examples

First, let's see OS and memory information:

![pysos run with -om](http://i.imgur.com/EBF3pw0.png)

We can see that the system has a slightly high load average for the CPU resources available for it, and that of the 4GB installed, 3.26 are currently in use, 0.33 is cached and so forth. Note that here `used` memory means that which is *actually* in use, not what is marked as used but is simply cached. Similarly `cached` memory reported is what is cached by the system and freely available.

Now let's see the BIOS information for this system as reported by `dmidecode`

![pysos run with -b](http://i.imgur.com/FYjRb93.png)

This will report known information about the BIOS, the physical system itself (manufacturer, serial, model, etc...) and the CPU layout and memory controller information.


Now let's view some more interesting information, for example the virtualization information about this system. Note, for pysos 'virtualization information' implies that the system is either a hypervisor using KVM (with additional information for oVirt/RHEV hypervisors) or is a system managing an oVirt/RHEV deployment. This does **not** imply the system itself is virtualized, though that can and will be reported through other options like `-b`

![pysos run with -v](http://i.imgur.com/fxdLzUj.png)


###$THING doesn't work!

Please report it here, along with an example if possible!


###When will feature XYZ be implemented?

I'm always looking to expand pysos, but you're more than welcome to submit patches for features yourself.

It's also good to know that if a sosreport doesn't capture the information, pysos would not be able to report on it. I am playing with the idea of getting pysos to run locally, but the main focus is parsing through sosreports.

Currently this is the (unordered) list of things I still want to implement directly into pysos:

 - Proper (read: actual) LVM information
 - Common sysctls to look at, and the ability to filter for specific sysctls
 - An integrated updater
 - A proper `setup.py` installer
 - Satellite information
 - Work with sosreport tarballs, not just the extracted directory
