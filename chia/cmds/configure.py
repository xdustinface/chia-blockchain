from pathlib import Path
from typing import Dict

import click

from chia.util.config import load_config, save_config, str2bool
from chia.util.default_root import DEFAULT_ROOT_PATH


def configure(
    root_path: Path,
    set_farmer_peer: str,
    set_node_introducer: str,
    set_fullnode_port: str,
    set_log_level: str,
    enable_upnp: str,
    set_outbound_peer_count: str,
    set_peer_count: str,
    testnet: str,
):
    config: Dict = load_config(DEFAULT_ROOT_PATH, "config.yaml")
    change_made = False
    if set_node_introducer:
        try:
            if set_node_introducer.index(":"):
                host, port = (
                    ":".join(set_node_introducer.split(":")[:-1]),
                    set_node_introducer.split(":")[-1],
                )
                config["full_node"]["introducer_peer"]["host"] = host
                config["full_node"]["introducer_peer"]["port"] = int(port)
                config["introducer"]["port"] = int(port)
                print("Node introducer updated")
                change_made = True
        except ValueError:
            print("Node introducer address must be in format [IP:Port]")
    if set_farmer_peer:
        try:
            if set_farmer_peer.index(":"):
                host, port = (
                    ":".join(set_farmer_peer.split(":")[:-1]),
                    set_farmer_peer.split(":")[-1],
                )
                config["full_node"]["farmer_peer"]["host"] = host
                config["full_node"]["farmer_peer"]["port"] = int(port)
                config["harvester"]["farmer_peer"]["host"] = host
                config["harvester"]["farmer_peer"]["port"] = int(port)
                print("Farmer peer updated, make sure your harvester has the proper cert installed")
                change_made = True
        except ValueError:
            print("Farmer address must be in format [IP:Port]")
    if set_fullnode_port:
        config["full_node"]["port"] = int(set_fullnode_port)
        config["full_node"]["introducer_peer"]["port"] = int(set_fullnode_port)
        config["farmer"]["full_node_peer"]["port"] = int(set_fullnode_port)
        config["timelord"]["full_node_peer"]["port"] = int(set_fullnode_port)
        config["wallet"]["full_node_peer"]["port"] = int(set_fullnode_port)
        config["wallet"]["introducer_peer"]["port"] = int(set_fullnode_port)
        config["introducer"]["port"] = int(set_fullnode_port)
        print("Default full node port updated")
        change_made = True
    if set_log_level:
        levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
        if set_log_level in levels:
            config["logging"]["log_level"] = set_log_level
            print(f"Logging level updated. Check {DEFAULT_ROOT_PATH}/log/debug.log")
            change_made = True
        else:
            print(f"Logging level not updated. Use one of: {levels}")
    if enable_upnp is not None:
        config["full_node"]["enable_upnp"] = str2bool(enable_upnp)
        if str2bool(enable_upnp):
            print("uPnP enabled")
        else:
            print("uPnP disabled")
        change_made = True
    if set_outbound_peer_count is not None:
        config["full_node"]["target_outbound_peer_count"] = int(set_outbound_peer_count)
        print("Target outbound peer count updated")
        change_made = True
    if set_peer_count is not None:
        config["full_node"]["target_peer_count"] = int(set_peer_count)
        print("Target peer count updated")
        change_made = True
    if testnet is not None:

        daemon_port = 55400
        farmer_port = 8447
        farmer_rpc_port = 8559
        harvester_port = 8448
        harvester_rpc_port = 8560
        full_node_port = 8444
        full_node_rpc_port = 8555
        introducer_port = 8445
        wallet_port = 8449
        wallet_rpc_port = 9256
        timelord_launcher_port = 8000
        timelord_port = 8446
        ui_port = 8222

        introducer = "introducer.chia.net"
        selected_network = "mainnet"

        if testnet == "true" or testnet == "t":
            print("Setting Testnet")

            daemon_port = 55401
            farmer_port = 58447
            farmer_rpc_port = 58559
            harvester_port = 58448
            harvester_rpc_port = 58560
            full_node_port = 58444
            full_node_rpc_port = 58555
            introducer_port = 58445
            wallet_port = 58449
            wallet_rpc_port = 59256
            timelord_launcher_port = 58000
            timelord_port = 58446
            ui_port = 58222

            introducer = "beta1_introducer.chia.net"
            selected_network = "testnet7"
        elif testnet == "false" or testnet == "f":
            print("Setting Mainnet")
        else:
            print("Please choose True or False")
            return 1

        config["daemon_port"] = daemon_port

        config["farmer"]["port"] = farmer_port
        config["farmer"]["rpc_port"] = farmer_rpc_port
        config["farmer"]["full_node_peer"]["port"] = full_node_port
        config["farmer"]["harvester_peer"]["port"] = harvester_port
        config["farmer"]["selected_network"] = selected_network

        config["full_node"]["port"] = full_node_port
        config["full_node"]["rpc_port"] = full_node_rpc_port
        config["full_node"]["farmer_peer"]["port"] = farmer_port
        config["full_node"]["introducer_peer"]["host"] = introducer
        config["full_node"]["introducer_peer"]["port"] = full_node_port
        config["full_node"]["timelord_peer"]["port"] = timelord_port
        config["full_node"]["wallet_peer"]["port"] = wallet_port
        config["full_node"]["selected_network"] = selected_network

        config["harvester"]["port"] = harvester_port
        config["harvester"]["rpc_port"] = harvester_rpc_port
        config["harvester"]["farmer_peer"]["port"] = farmer_port
        config["harvester"]["selected_network"] = selected_network

        config["introducer"]["port"] = introducer_port
        config["introducer"]["selected_network"] = selected_network

        config["pool"]["selected_network"] = selected_network

        config["timelord"]["port"] = timelord_port
        config["timelord"]["full_node_peer"]["port"] = full_node_port
        config["timelord"]["vdf_server"]["port"] = timelord_launcher_port
        config["timelord"]["selected_network"] = selected_network

        config["timelord_launcher"]["port"] = timelord_launcher_port

        config["ui"]["daemon_port"] = daemon_port
        config["ui"]["port"] = ui_port
        config["ui"]["rpc_port"] = full_node_rpc_port
        config["ui"]["selected_network"] = selected_network

        config["wallet"]["port"] = wallet_port
        config["wallet"]["rpc_port"] = wallet_rpc_port
        config["wallet"]["full_node_peer"]["port"] = full_node_port
        config["wallet"]["introducer_peer"]["port"] = introducer_port
        config["wallet"]["selected_network"] = selected_network

        config["selected_network"] = selected_network

        print("Default full node port, introducer and network setting updated")
        change_made = True

    if change_made:
        print("Restart any running chia services for changes to take effect")
        save_config(root_path, "config.yaml", config)
    return 0


@click.command("configure", short_help="Modify configuration")
@click.option(
    "--testnet",
    "-t",
    help="configures for connection to testnet",
    type=click.Choice(["true", "t", "false", "f"]),
)
@click.option("--set-node-introducer", help="Set the introducer for node - IP:Port", type=str)
@click.option("--set-farmer-peer", help="Set the farmer peer for harvester - IP:Port", type=str)
@click.option(
    "--set-fullnode-port",
    help="Set the port to use for the fullnode, useful for testing",
    type=str,
)
@click.option(
    "--set-log-level",
    "--log-level",
    "-log-level",
    help="Set the instance log level",
    type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]),
)
@click.option(
    "--enable-upnp",
    "--upnp",
    "-upnp",
    help="Enable or disable uPnP",
    type=click.Choice(["true", "t", "false", "f"]),
)
@click.option(
    "--set_outbound-peer-count",
    help="Update the target outbound peer count (default 8)",
    type=str,
)
@click.option("--set-peer-count", help="Update the target peer count (default 80)", type=str)
@click.pass_context
def configure_cmd(
    ctx,
    set_farmer_peer,
    set_node_introducer,
    set_fullnode_port,
    set_log_level,
    enable_upnp,
    set_outbound_peer_count,
    set_peer_count,
    testnet,
):
    configure(
        ctx.obj["root_path"],
        set_farmer_peer,
        set_node_introducer,
        set_fullnode_port,
        set_log_level,
        enable_upnp,
        set_outbound_peer_count,
        set_peer_count,
        testnet,
    )
