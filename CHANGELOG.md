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