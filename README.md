# Weekly roles of the Packit team

This repository handles the weekly rotating roles of the Packit team.
Rotating roles represent work that needs to be done each week (e.g. releasing, 
monitoring, communicating with the users). They are described in the issues labelled with `roles`.
These issues are automatically cloned every Friday and team members are assigned to them. 

The repository contains:
- `clone_roles.py` - script that does the cloning of the issues, assigning of the team members 
and closing the old ones
- `.github/workflows/rotate_roles.yaml` - Github action that runs the script periodically (each Friday)

