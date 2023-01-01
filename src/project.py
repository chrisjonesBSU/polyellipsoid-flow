"""Define the project's workflow logic and operation functions.

Execute this script directly from the command line, to view your project's
status, execute operations and submit them to a cluster. See also:

    $ python src/project.py --help

"""
import signac
from flow import FlowProject, directives
from flow.environment import DefaultSlurmEnvironment
import os


class MyProject(FlowProject):
    pass


class Borah(DefaultSlurmEnvironment):
    hostname_pattern = "borah"
    template = "borah.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="shortgpu",
            help="Specify the partition to submit to."
        )


class R2(DefaultSlurmEnvironment):
    hostname_pattern = "r2"
    template = "r2.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="shortgpuq",
            help="Specify the partition to submit to."
        )


class Fry(DefaultSlurmEnvironment):
    hostname_pattern = "fry"
    template = "fry.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="batch",
            help="Specify the partition to submit to."
        )

# Definition of project-related labels (classification)
@MyProject.label
def finished(job):
    return job.doc.done


@MyProject.label
def initialized(job):
    return job.isfile("sim_traj.gsd")


@directives(executable="python -u")
@directives(ngpu=1)
@MyProject.operation
@MyProject.post(finished)
def sample(job):
    from polyellipsoid import System, Simulation
    from cmeutils.gsd_utils import ellipsoid_gsd


    with job:
        print("-------------------------------")
        print("JOB ID NUMBER:")
        print(job.id)
        print("-------------------------------")
        print()
        print("-------------------------------")
        print("Creating the system...")
        print("-------------------------------")
        print()
        system = System(
                n_chains=job.sp.n_chains,
                chain_lengths=job.sp.chain_lengths,
                bead_length=job.sp.bead_length,
                bead_mass=job.sp.bead_mass,
                density=job.sp.density
                bond_length=job.sp.bond_length,
        )
        if job.sp.system_type == "pack":
            system.pack(**job.sp.kwargs)
        elif job.sp.system_type == "stack":
            system.stack(**job.sp.kwargs)

        print("-------------------------------")
        print("Creating the simulation...")
        print("-------------------------------")
        print()
        sim = Simulation(
                system,
                epsilon=job.sp.epsilon,
                lperp=job.sp.lperp,
                lpar=job.sp.lpar,
                bond_k=job.sp.bond_k,
                r_cut=job.sp.r_cut,
                angle_k=job.sp.angle_k,
                angle_theta=job.sp.angle_theta,
                seed=job.sp.sim_seed,
                gsd_write=10000,
                log_write=1000
        )

        # Write your simulation procedure below:

        # Run a shrink simulation is all of the shrink params are defined:
        if all(
                [job.sp.init_shrink_kT, job.sp.final_shrink_kT, 
                 job.sp.shrink_steps, job.sp.shrink_period]
        ):
            shrink_kT = sim.temperature_ramp(
                    n_steps=job.sp.shrink_steps,
                    kT_start=job.sp.init_shirnk_kT,
                    kT_final=job.sp.final_shrink_kT,
                    period=job.sp.shrink_period
            )

            sim.run_shrink(
                    kT=shrink_kT,
                    tau_kt=job.sp.tau_kt,
                    n_steps=job.sp.shrink_steps,
                    shrink_period=job.sp.shrink_period
            )

            hoomd.write.GSD.write(
                    sim.sim.state, filename=os.path.join(job.ws, "shrink.gsd")
            )


if __name__ == "__main__":
    MyProject().main()
