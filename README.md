# Utility functions to make working with SLURM easier

## Installation

The recommended way to install **kslurm** is via [`pipx`](https://pypa.github.io/pipx), a tool for installing Python applications. This ensures kslurm is globally available without affecting your global Python environment. Installation instructions for pipx can be found on their [website](https://pypa.github.io/pipx).
Once pipx is installed, run:
```bash
pipx install kslurm
```
> **Note:** kslurm requires Python 3.9 or higher. If pipx was installed using an older Python version (e.g. 3.8), you must specify the correct Python executable. First, activate the appropriate Python version (for example, `module load python/3.10`) so that `python --version` shows 3.9 or higher. 
Then run:
```bash
pipx install kslurm --python $(which python)
```
To enable full kslurm features (including integration with `pip`), source the init script, preferably in your `~/.bash_profile` (the init script may contain commands unavailable on non-login nodes). 
Run:
```bash
kpy bash >> $HOME/.bash_profile
```
Finally, complete the basic configuration:
1. **Set your SLURM account.**  
   Run:
```bash
kslurm config account -i
```
This starts an interactive session listing the accounts available to you. Each account shows its LevelFS, the higher the LevelFS => the more underused the account is, so choose accounts with higher values.
2. **Set your pip directory.**  
This directory stores Python wheels and virtual environments. It should be in permanent storage or a project directory (e.g., on ComputeCanada servers, use `~/projects/<account_name>/<user_name>/.kslurm`). Run:
```bash
kslurm config pipdir <dir>
```

## Upgrading and Uninstalling

- To update kslurm:
```bash
pipx upgrade kslurm
```
- To remove kslurm:
```bash
pipx uninstall kslurm
```

## Neuroglia-helpers Integration

See the [dedicated page](docs/neuroglia-helpers.md).

## Legacy Installer

kslurm includes an installation script that was previously the recommended method. While it may still work, it is no longer supported and may be removed in the future. Its instructions are provided here for reference. Users who installed kslurm via this script should switch to pipx for long-term support. Simply uninstall kslurm using the instructions below, then install via pipx as described above.

- **Install:**  
```
curl -sSL https://raw.githubusercontent.com/pvandyken/kslurm/master/install_kslurm.py | python -
```
- **Uninstall:**  
```
curl -sSL https://raw.githubusercontent.com/pvandyken/kslurm/master/install_kslurm.py | python - --uninstall
```
- **Update:**  
```
kslurm update
```

## Installing via Git Clone

To install kslurm, clone the repository with the --recursive option:
```
git clone --recursive https://github.com/pvandyken/kslurm.git
```

## Features

kslurm currently offers four commands:

- **kbatch:** Batch submission jobs (no immediate output)  
- **krun:** Interactive submission  
- **kjupyter:** Jupyter sessions  
- **kpy:** Python environment management  

These commands use regex-based argument parsing, so instead of writing a SLURM file or supplying confusing `--arguments`, you can request resources with an intuitive syntax:
```
krun 4 3:00 15G gpu=v100:2
```

This command requests an interactive session with **4 cores**, for **3 hours**, using **15 GB** of memory, and **2 GPU** instances of the **v100**.

Anything not specified falls back to a default. By default, commands request a 3 hr job with 1 core, 4 GB of memory, and no GPU. You can also run a predefined job template using `-j <template>`. Run any command with `-J` to list all templates. Any template values can be overridden by providing the appropriate argument.

The full list of possible requests, their syntax, and defaults is at the end of this README.

---

### krun

`krun` is used for interactive sessions on the cluster. Running `krun` without arguments starts an interactive session:
```
krun
```

You will notice your terminal prompt changes to the assigned cluster node. To end the session, use the `exit` command.
You can also submit a specific program to run:
```
krun 1:00 1G python my_program.py
```

This requests a **1 hr** session with **1 core** and **1 GB** of memory. The job's output appears on the console. Note that your terminal is tied to the job, if you quit or get disconnected, your job ends. (Using `tmux` can help; see this [tutorial from Yale](https://docs.ycrc.yale.edu/clusters-at-yale/guides/tmux/) for more details.)

> **Reminder:** Never request more time than your cluster administrator's recommended maximum for interactive jobs. For ComputeCanada servers, do not request more than **3 hr**. Exceeding that places you in the general pool for resource assignment, and your job could take hours to start. Jobs of **3 hr or less** typically start quickly without too much wait time.

---

### kbatch

Use `kbatch` for jobs that don't require immediate output monitoring or run longer than three hours. This command schedules the job and returns control of the terminal. Output goes to a file named `slurm-[jobid].out` in your current directory.

`kbatch` improves on `sbatch` by not requiring a script file. You can submit a command directly:
```
kbatch 2-00:00 snakemake --profile slurm
```

This schedules a **2 day** job running **snakemake**.

For more complex jobs, you can still use a script. Note that `kbatch` explicitly specifies resources it knows about on the command line. Command-line arguments override `#SBATCH` directives in the submit script. Currently, you cannot request resources via `#SBATCH` directives unless they’re not supported by kslurm (this may change in future releases).

---

### kjupyter

`kjupyter` requests an interactive job running a Jupyter server. Like with `krun`, do not request more time than the recommended maximum (3 hr for ComputeCanada). If you need more time, start a new job when the old one expires.

Include the `--venv` flag to request a saved virtual environment (see `kpy save`). Jupyter starts in the specified environment. `jupyter-lab` should already be installed in that venv:
```
kjupyter 32G 2 --venv <your_venv_name>
```
This starts a Jupyter session with **32 GB** of memory and **2 cores**.

If no venv is specified, `kjupyter` assumes `jupyter-lab` is available on the `$PATH`. This is useful for running a global Jupyter or a Jupyter installed in an active venv. Note that without a venv, Jupyter won't install on local scratch, so performance may be slower.

---

## kpy

`kpy` provides tools to manage pip virtual environments on SLURM compute clusters, addressing issues unique to such servers:

- **Ephemeral venvs:**  
  On compute clusters, Python venvs are usually installed on local scratch storage, making them ephemeral. Installing a venv can take time, so `kpy` lets you archive entire venvs for permanent storage (e.g., on project-specific or home directories). Once saved, venvs can be quickly reloaded in a new compute environment. Copying venvs between locations is not trivial; this approach has been tested on ComputeCanada servers, but other environments may present issues.

- **No internet on compute nodes:**  
  Compute nodes often lack internet access, limiting installation to locally available wheels. With `kpy`, venvs can be created on login nodes (with internet access), then saved and loaded on compute nodes. `kpy` also includes optional bash tools (see `kpy bash`), including a pip wrapper that prevents internet access on compute nodes and links pip to a local wheelhouse.

### Commands

#### `create`

```
kpy create [<version|3.x>] [<name>]
```

Create a new environment. The name is optional; if not provided, a placeholder name is generated. The version must be `3.x` (e.g., `3.8`, `3.10`). The corresponding Python executable must be on your PATH (e.g., `python3.8`). If no version is provided, the Python version used to install kslurm is used.

- On a login node, the venv is created in `$TMPDIR`.  
- On a compute node, it is created in `$SLURM_TMPDIR`.

#### `save`

```
kpy save [-f] <name>
```

Save the venv to your permanent cache. This requires setting `pipdir` in the kslurm config (see above). By default, `save` won't overwrite an existing cache; use `-f` to force overwrite. If a new name is provided, it updates the current venv's name and prompt.

#### `load`

```
kpy load [<name>] [--as <newname>]
```

Load a saved venv from the cache. If a venv with `<name>` already exists, the command fails because each name is unique. Use `--as <newname>` to load under a different name (the saved venv's name remains the same). Running `kpy load` without a name lists all cached venvs.

#### `activate`

```
kpy activate [<name>]
```


Activate a venv created by `create` or loaded by `load`. The name is the venv’s prompt name (provided on creation, via `--as`, or by the last save). This command only works on a compute node. Venvs created on a login node cannot be directly activated on a compute node—load them first.

Running `kpy activate` without a name lists the venvs available for activation.

#### `list`

```
kpy list
```

List all saved venvs (i.e., those you can `load`).

#### `rm`

```
kpy rm <name>
```

Delete a saved venv.

#### `bash`

```
kpy bash
```

Echoes a line of bash script to add to your `~/.bashrc`:

```
kpy bash >> $HOME/.bashrc
```

This adds features to your command line environment:

- **pip wrapper:** Detects if you are on a login node when running `install`, `wheel`, or `download`. If not on a login node, appends `--no-index` to prevent internet access.
- **wheelhouse management:** If `pipdir` is set in the kslurm config, a wheelhouse is created in your pip directory. Wheels downloaded via `pip wheel` go into that wheelhouse, and all wheels there are discoverable by `pip install`, both on login and compute nodes.

---

## Kapp

Kapp provides tools to manage Singularity containers. Pull images from Docker Hub without worrying about image size, duplicate pulls, or tracking whether `:latest` is up to date. Kapp manages your `.sif` image files so you can run them from anywhere on the cluster without managing environment variables or remembering paths. Kapp-managed images integrate seamlessly with Snakemake using the `--singularity-prefix` directory.

### `pull`

```
kapp pull <image_uri> [-a <alias>] [--mem <memory>]
```

Pull an image from a repository. Currently, only Docker Hub is supported. The image URI format is:

```
[<scheme>://[<organization>/]<repo>:<tag>]
```
Examples:
```
docker://ubuntu:latest
nipreps/fmriprep:21.0.2
busybox:latest
```

- The scheme is optional (defaults to `docker`).
- The organization is omitted for official Docker images.

When you call `kapp pull`, the tag resolves to the specific container it points to. Pulling multiple tags that point to the same container (e.g., `:latest` and its version tag) downloads the container only once. If tags update (e.g., `:latest` moves to a new release), `kapp pull` fetches the latest version, even if you’ve pulled that tag before.

Use `-a <alias>` to set an alias for the URI. You can then use the alias instead of the URI in future kapp commands (except `kapp pull`). For example:

```
kapp pull nipreps/fmriprep:latest -a fmriprep
kapp run fmriprep
```

Building `.sif` files from Docker containers can require significant memory and resources, making it unsuitable for login nodes. Kapp first downloads the container on the login node, then schedules a build step on an interactive compute node. It attempts to estimate required memory; if a build fails due to insufficient memory, specify a larger amount using `--mem <memory>`. Very small containers are built directly on the login node without a compute step.

---

### `path`

```
kapp path <uri_or_alias>
```

Prints the path of the specified container. This makes it easy to use kapp-managed containers with any Singularity command:

```
singularity -b /path/to/bind/dir $(kapp path my_container)
```

---

### `image`

```
kapp image (list|rm <uri_or_alias>)
```

- `kapp image list` lists all pulled containers.  
- `kapp image rm <container>` removes a container alias (and any aliases pointing to it). It does **not** remove the underlying data, since other tags might reference it. To delete dangling containers (those not referenced by any local URIs), use `kapp purge dangling`.

---

### `purge`

```
kapp purge dangling
```

Deletes all dangling image files (files not referenced by any local URIs) and removes any Snakemake aliases pointing to them.

---

### `alias`

```
kapp alias list
```

Lists all aliases currently in use and the containers they reference.

---

### `exec`, `shell`, `run`

```
kapp (exec|shell|run) <uri_or_alias> [args...]
```

Wrapper around `singularity (exec|shell|run)`. You cannot specify Singularity arguments—only container arguments. For Singularity options, call Singularity directly using `kapp path <container>` to get the container path. Most Singularity options (e.g., BIDS directory) can be set via environment variables, and `kapp` will consume them normally.

---

### `snakemake`

```
kapp snakemake
```

Prints the path to the Snakemake directory. Use this path with Snakemake’s `--singularity-prefix` option to let Snakemake consume containers downloaded by kapp. This is especially useful for cluster execution without internet: pull containers in advance on a login node, then use them in Snakemake later.

---

## Configuration

kslurm supports several configuration values, with more to come. All configuration is done via:

```
kslurm config <key> <value>
```

To print a configuration’s value:

```
kslurm config <key>
```

### Current values

- **account:** Default account for kslurm commands (`kbatch`, `krun`, etc).  
- **pipdir:** Directory to store cached venvs and wheels (should be a project or permanent storage directory).

## KSLURM Syntax

The full syntax is outlined below. You can always run a command with `-h` to get help.

| Resource  | Syntax                | Default  | Description                                    |
| --------- | --------------------- | -------- | ---------------------------------------------- |
| Time      | `[d-]dd:dd` - `d-hh:mm` | 3 hr     | Amount of time requested                     |
| CPUs      | `d`                   | 1        | Number of CPUs requested                      |
| Memory    | `d(G/M)[B]` (e.g. `4G`, `500MB`) | 4 GB     | Amount of memory requested                    |
| Account   | `--account <name>`    | -        | SLURM account to use (default can be set via `kslurm config account <account_name>`) |
| GPU       | `gpu=<type>:<number>` | 0        | GPU type and number (e.g. `gpu=v100:2`)         |
| Directory | `<valid directory>`   | `./`     | Change working directory before submitting the job |
| x11       | `--x11`               | False    | Request X11 forwarding for GUI applications    |

---
## Unsupported KSLURM Arguments

Currently, the only way to supply SLURM arguments beyond those listed below is to include them as `#SBATCH --directive` lines in a submission script. This only works with `kbatch`, not with `krun` or `kjupyter`. A future release may allow specifying these arguments directly on the command line. If you frequently use an option not listed below, open an issue and we can discuss adding support.

---
