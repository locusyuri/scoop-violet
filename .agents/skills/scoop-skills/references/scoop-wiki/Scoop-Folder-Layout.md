_Article stub. Please fill out/correct as needed. Maybe this is already or better documented elsewhere, in that case remove/redirect._

For general understanding and troubleshooting it can be helpful to know what folders Scoop uses and where they are. These are examples, configuration options could change where they are on your machine.

`%USERPROFILE%\scoop` - per user root location (default). Can be overridden via `%SCOOP%`.<br/>
`%ProgramData%\scoop` - root location of apps installed for all users. Can be overridden via `%SCOOP_GLOBAL%`.

`...\scoop\apps` - installed applications<br/>
`...\scoop\apps\scoop` - the Scoop application itself<br/>
`...\scoop\buckets` - manifests of installable apps (also a git clone of the bucket source repositories)<br/>
`...\scoop\cache` - the downloaded installers<br/>
`...\scoop\persist` - persisted application files<br/>
`...\scoop\shims` - added to PATH, wrappers that point to the installed applications<br/>

`%USERPROFILE%\.config\scoop` - Scoop configuration settings.




