import os
import json
import requests
import argparse
import textwrap
from typing import Union


def get_latest_mcpaper_server_url() -> Union[str, None]:
    versions_page = 'https://api.papermc.io/v2/projects/paper'
    headers = {
        'Accept': 'application/json',
    }

    latest_build = ''
    latest_version = ''
    download_url = None
    version_builds_url = ''

    # Get latest list of versions
    try:
        r = requests.get(versions_page, timeout=10,
                         headers=headers).content.decode()
        latest_version = json.loads(r)['versions'][-1]
    except Exception as e:
        print('Failed to find latest version of Paper MC: {}'.format(e))
        return None

    # Construct version builds URL
    version_builds_url = 'https://api.papermc.io/v2/projects/paper/versions/{}/builds/'.format(
        latest_version, )

    # Get latest list of builds for this version
    try:
        r = requests.get(version_builds_url, timeout=10,
                         headers=headers).content.decode()
        latest_build = json.loads(r)['builds'][-1]['build']
    except Exception as e:
        if latest_version != '':
            print('Failed to find the latest build of Paper MC version {}: {}'.format(
                latest_version, str(e)
            ))
        else:
            print('Failed to find the latest build of Paper MC: {}'.format(
                str(e)
            ))
        return None

    # Construct the download URL (hopefully they dont fk me here...)
    download_url = 'https://api.papermc.io/v2/projects/paper/versions/{}/builds/{}/downloads/paper-{}-{}.jar'.format(
        latest_version,
        latest_build,
        latest_version,
        latest_build, )
    return {
        'version': latest_version,
        'file': download_url.split('/')[-1],
        'url': download_url
    }


def download_file(url: str, output: str) -> bool:
    ok = False
    try:
        r = requests.get(url)
        with open(output, 'wb') as f:
            f.write(r.content)
        ok = True
    except Exception as e:
        print('Failed to write file {}: {}'.format(output, str(e)))
    return ok


if __name__ == "__main__":

    output_directory = os.path.join(os.getcwd())

    parser = argparse.ArgumentParser(
        prog='Minecraft Server Updater (Paper Minecraft)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='',
    )

    parser.add_argument(
        '--dir', '-d',
        action='store',
        help='Directory to write the latest server JAR to.',
    )

    args = parser.parse_args()

    if args.dir != None:
        if os.path.isdir(args.dir):
            output_directory = args.dir
        else:
            print('No such directory: {}'.format(args.dir))

    print('Writing server to directory: {}'.format(output_directory))
    output_jar = os.path.join(output_directory, 'server.jar')
    print('Finding latest server version...', end='', flush=True)
    result = get_latest_mcpaper_server_url()
    print('Ok. [Latest: v{}]'.format(result['version']))
    print('Downloading server JAR to: {}'.format(output_jar))
    download_file(result['url'], output_jar)
    if os.path.isfile(output_jar):
        print('Done.')
    else:
        print('Fail.')
