### Prerequisites

**PowerShell 5.1 or later is required**.

If you're on Windows 10 or Windows Server 2016 or any newer version of Windows OS, you should be all set. For Windows 7/8 and Windows Server 2008/2012 by installing [Windows Management Framework 5.1](https://aka.ms/wmf5download) the OS-bundled PowerShell can be upgraded to version 5.1<sup>[windows powershell system requirements]</sup>, or you may install the latest version of PowerShell that supports your system side-by-side. Other older versions of Windows OS are not supported.

PowerShell version check:
```powershell
$PSVersionTable.PSVersion # has to be >= 5.1
```

**Appropriate execution policy**

Make sure you have allowed PowerShell to execute local scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

`Unrestricted` will work too, but it is less secure. So stick with `RemoteSigned` if you're not sure.

### Installing Scoop

Typically, in a PowerShell command console, run:

```powershell
irm get.scoop.sh | iex
```

For advanced installation such as installing Scoop to a custom location other than the default path, please refer to [the installer's README].

### Using Scoop
Although Scoop is written in PowerShell, its interface is closer to Git and Mercurial than it is to most PowerShell programs.

To get an overview of Scoop's interface, run:

    scoop help

You'll see a list of commands with a brief summary of what each command does. For more detailed information on a command, run `scoop help <command>`, e.g. `scoop help install` (try it!).

Now that you have a rough idea of how Scoop commands work, let's try installing something.

    scoop install curl

You'll probably see a warning about a missing hash, but you should see a final message that cURL was installed successfully. Try running it:

    curl -L https://get.scoop.sh

You should see some HTML, probably with a 'document moved' message. Note that, like when you installed Scoop, you didn't need to restart your console for the program to work. Also, if you've installed cURL manually before you might have noticed that you didn't get an error about SSL—Scoop downloaded a certificate bundle for you.

##### Finding apps
Let's say you want to install the `ssh` command but you're not sure where to find it. Try running:
    
    scoop search ssh

You'll should see a result for 'openssh'. This is an easy case because the name of the app contains 'ssh'.

You can also find apps by the name of the commands they install. For example,

    scoop search hg

This shows you that the 'mercurial' app includes 'hg.exe'.

### Updating Scoop
To get the latest version of Scoop you have to run the command

    scoop update

This will download the latest version of scoop and update the local app manifests.

The `scoop update` will be automatically run after its last run to keep scoop updated if you call `scoop install <app>`, `scoop update <app>`, `scoop download <app>` or `scoop virustotal <app>`.

After you updated Scoop, you can update individual apps

    scoop update curl

If you want to update all your installed apps, you can run

    scoop update *

[windows powershell system requirements]: https://learn.microsoft.com/en-us/powershell/scripting/windows-powershell/install/windows-powershell-system-requirements
[the installer's README]: https://github.com/ScoopInstaller/Install