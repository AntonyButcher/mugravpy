# mugravpy
## Processing Workflows

### 1. Processing

- 

# Installation

python setup.py develop


# Developer notes

## Using a branch for development:

It is recomended that anyone developing this package opens a branch, makes their changes, then merges the branch. The steps are as follows: 
   1.	Create branch for desired feature/change \
       1.	E.g. **git branch calc-divide** (creates branch) \
       2.	(**git branch** lists all branches) 
   2.	Then check out branch (to work on it): \
       1.	E.g. **git checkout calc-divide** 
   3.	Then work on changes… 
   4.	Then commit changes (locally): \
       1.	**git add -A**  \
       2.	**git commit -m “Added divide func”** 
   5.	Push/commit to remote repository: \
       1.	**git push -u origin calc-divide** 
           1.	(pushs calc-divide branch to remote repository) 
           2.	Can view branchs using **git branch -a** 
   6.	Then can check branch and then merge with master (can do this locally or on github remote repository) 
   7.	Merge with master: \
       1.	**git checkout master** \
       2.	**git pull origin master** \
       3.	**git branch --merged** (states which branches have enn merged) \
       4.	**git merge calc-divide** (changes are merged to master on local) \
       5.	**git push origin master** (changes are pushed from local to remote repository) 
   8.	Can then delete branch: 
   9.	Check merged: \
       1.	**git branch --merged** (check that branch is merged) \
       2.	**git branch -d calc-divide** (deletes branch locally) \
       3.	**git branch -a** (checks that done) \
       4.	**git push origin --delete calc-divide** (deletes branch on remote repository) 

End of readme.
