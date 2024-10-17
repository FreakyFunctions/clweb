# clweb: preserver
cloneweb/clweb is to scrape/preserve a webpage and its css and javascript contents.
## q&a
q: should we use this in production<br>
a: no, it is not stable<br>
q: is it still being worked on<br>
a: yes
## bugs
css isn't being saved for some reason.<br>
random characters being saved in the scraped code<br>
its not removing trailing even though we are using strip via the process.<br>
there is no way to check if a folder or file exists yet so it errors.
## coming soon
- img saving
- css saving fixes
- js and css trailing fixing, etc.
- ability to spread through all files and download those needed.
- saving folders like the ones in the links.
## limitations
clweb can't do a lot. i mean its made in python ffs.<br>
if i rewrote in node js, it would probably be 10,000x better but why not take the hard approach.
## test files
test files for clweb will appear like fixing files with gpt, etc. soon!