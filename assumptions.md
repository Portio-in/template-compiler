### Folder structure

| Folder Name  | Details |
|--------|--------|
| base | This folder will consist all base templates for an particular template and will not be considered at compile time  [Mainly those parts used with {% extends __ %}] |
| partials | This folder will consist all partial templates for an particular template and will not be considered at compile time [Mainly those parts used with {% include __ %}]|
| ignoreme | all files of this folder will be ignored at compile time |
| . | All other template in base directory will be considered for compilation |

---
### Routing 
- File based routing will be used
- All files will be considered as a route
- index.html will be considered as route / also as /index
- except that other files will be considered as /<filename_without_extension>

---
### CSS , JS and other static files
- Images or other files : All images and other files will be served from S3 directly
- CSS & JS will be delivered by [jsDelivr](https://www.jsdelivr.com/) and fill will be managed by an repository of organization
---
 
### TODOS
- [ ] Create a repository for jsDelivr
- [ ] Support to generate multiple pages based on config . Like some template may have requirement to generate multiple pages based on some config [projects page]

----
Random thoughts

Multi page elements will be 0 index based ordering
config.json will hold multi page configurations