# Weekly roles of the Packit team

![Sharing responsibility in a team](./img/title.png)

This repository handles the weekly rotating roles of the Packit team.
Rotating roles represent work that needs to be done each week (e.g. releasing,
monitoring, communicating with the users). They are described in [issues using the `roles` label](https://github.com/packit/agile/issues?q=is%3Aissue+is%3Aopen+label%3Aroles).
These issues are automatically cloned every Friday and team members are assigned to them.

The repository contains:

1. `clone_roles.py` - script that does the cloning of the issues, assigning of the team members
   and closing the old ones
2. `.github/workflows/rotate_roles.yaml` - Github action that runs the script periodically (each Friday)

You can read more about the process in the following blog post series:

- [How to run an open-source service?](https://medium.com/@laura.barcziova/how-to-run-an-open-source-service-fb3303240e69)
- [Inception of rotating roles](https://medium.com/@laura.barcziova/inception-of-rotating-roles-9caf971b3096)
- [Share team responsibilities efficiently](https://medium.com/@laura.barcziova/share-team-responsibilities-efficiently-9a202aad7bd0)
- [Role rotation tutorial](https://medium.com/@laura.barcziova/role-rotation-tutorial-957ed3545ef2)
