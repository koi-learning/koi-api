# Changelog
## 0.3
### 0.3.1
- critical Bugfix when accessing users
### 0.3.2
- propagate added samples through instance etags (adding samples with to instances would not trigger workers to retrain as thy indefinitly refresh the instance as untrainable.)
### 0.3.3
- add last_modified property to instances and models.
## 0.4
- added `/health` node to reflect the koi_system being up and running
- changed all import to absolute
### 0.4.1
- quickfix for changes in flask 2.2.0 that break our code
### 0.4.2
- removed setup.py
- added pyproject.toml
- set versions of dependencies fixed
### 0.4.3
- changed some dt.now() to dt.utcnow()
### 0.4.4
- added new field for instance: has_requests -> is used by PWA to show open requests in instance overview
### 0.4.5
- added a new workflow for releases
- added configuration through environment variables starting with KOI_
- updated the Dockerfile and added automatic releases for docker images.