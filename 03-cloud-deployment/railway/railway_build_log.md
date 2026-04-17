```
(ai_env) lc_thanh@DESKTOP-IHAC4I0:~/ai/lab12_2A202600091/03-cloud-deployment/railway$ railway link
> Select a workspace Le Cong Thanh's Projects
> Select a project lab12
> Select an environment production
> Select a service <esc to skip> lab12

Project lab12 linked successfully! 🎉
(ai_env) lc_thanh@DESKTOP-IHAC4I0:~/ai/lab12_2A202600091/03-cloud-deployment/railway$ railway up
  Indexed                                                                                     
  Compressed [====================] 100%                                                      
  Uploaded                                                                                      Build Logs: https://railway.com/project/74d1c42e-cc90-4e18-8feb-531bb61d0b2b/service/ff3b4317-d2ed-44f7-a79b-85549fe1fbb3?id=e0b97add-e277-43c4-8c15-ed939d8ce412&
scheduling build on Metal builder "builder-bccdni"
fetched snapshot sha256:ff71e2caf39d45bd0c64bb238dd54b80a8a32e30ea46af4ab5b4eb837d73f954 (2.2 kB bytes)
fetching snapshot
unpacking archive
using build driver nixpacks-v1.41.0

╔══════════════════════════════ Nixpacks v1.41.0 ══════════════════════════════╗
║ setup      │ python3, gcc                                                    ║
║──────────────────────────────────────────────────────────────────────────────║
║ install    │ python -m venv --copies /opt/venv && . /opt/venv/bin/activate   ║
║            │ && pip install -r requirements.txt                              ║
║──────────────────────────────────────────────────────────────────────────────║
║ start      │ uvicorn app:app --host 0.0.0.0 --port $PORT                     ║
╚══════════════════════════════════════════════════════════════════════════════╝


[internal] load build definition from Dockerfile
[internal] load build definition from Dockerfile
[internal] load metadata for ghcr.io/railwayapp/nixpacks:ubuntu-1745885067
[internal] load metadata for ghcr.io/railwayapp/nixpacks:ubuntu-1745885067
[internal] load .dockerignore
[internal] load .dockerignore
SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ARG "AGENT_API_KEY") (line 11)(https://docs.docker.com/go/dockerfile/rule/secrets-used-in-arg-or-env/)
 details: Sensitive data should not be used in the ARG or ENV commands

SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ENV "AGENT_API_KEY") (line 12)(https://docs.docker.com/go/dockerfile/rule/secrets-used-in-arg-or-env/)
 details: Sensitive data should not be used in the ARG or ENV commands

UndefinedVar: Usage of undefined variable '$NIXPACKS_PATH' (line 18)(https://docs.docker.com/go/dockerfile/rule/undefined-var/)
 details: Variables should be defined before their use

[stage-0 6/8] RUN --mount=type=cache,id=s/ff3b4317-d2ed-44f7-a79b-85549fe1fbb3-/root/cache/pip,target=/root/.cache/pip python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt
[stage-0 5/8] COPY . /app/.
[stage-0 4/8] RUN nix-env -if .nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix && nix-collect-garbage -d
[stage-0 3/8] COPY .nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix .nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix
[internal] load build context
[stage-0 2/8] WORKDIR /app/
[stage-0 1/8] FROM ghcr.io/railwayapp/nixpacks:ubuntu-1745885067@sha256:d45c89d80e13d7ad0fd555b5130f22a866d9dd10e861f589932303ef2314c7de
[internal] load build context
[stage-0 1/8] FROM ghcr.io/railwayapp/nixpacks:ubuntu-1745885067@sha256:d45c89d80e13d7ad0fd555b5130f22a866d9dd10e861f589932303ef2314c7de
[internal] load build context
[stage-0 3/8] COPY .nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix .nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix
[stage-0 5/8] COPY . /app/.
[stage-0 6/8] RUN --mount=type=cache,id=s/ff3b4317-d2ed-44f7-a79b-85549fe1fbb3-/root/cache/pip,target=/root/.cache/pip python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt
Collecting fastapi==0.115.0 (from -r requirements.txt (line 1))

  Downloading fastapi-0.115.0-py3-none-any.whl.metadata (27 kB)

  Downloading uvicorn-0.30.0-py3-none-any.whl.metadata (6.3 kB)

Collecting starlette<0.39.0,>=0.37.2 (from fastapi==0.115.0->-r requirements.txt (line 1))

Collecting pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4 (from fastapi==0.115.0->-r requirements.txt (line 1))

  Downloading pydantic-2.13.2-py3-none-any.whl.metadata (108 kB)

Collecting typing-extensions>=4.8.0 (from fastapi==0.115.0->-r requirements.txt (line 1))

  Downloading typing_extensions-4.15.0-py3-none-any.whl.metadata (3.3 kB)

Collecting click>=7.0 (from uvicorn==0.30.0->uvicorn[standard]==0.30.0->-r requirements.txt (line 2))

Collecting h11>=0.8 (from uvicorn==0.30.0->uvicorn[standard]==0.30.0->-r requirements.txt (line 2))

  Downloading httptools-0.7.1-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (3.5 kB)

Collecting python-dotenv>=0.13 (from uvicorn[standard]==0.30.0->-r requirements.txt (line 2))

Collecting pyyaml>=5.1 (from uvicorn[standard]==0.30.0->-r requirements.txt (line 2))

  Downloading pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.4 kB)

Collecting uvloop!=0.15.0,!=0.15.1,>=0.14.0 (from uvicorn[standard]==0.30.0->-r requirements.txt (line 2))

  Downloading uvloop-0.22.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (4.9 kB)

  Downloading watchfiles-1.1.1-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.9 kB)

Collecting websockets>=10.4 (from uvicorn[standard]==0.30.0->-r requirements.txt (line 2))

  Downloading annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)

Collecting pydantic-core==2.46.2 (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4->fastapi==0.115.0->-r requirements.txt (line 1))

  Downloading pydantic_core-2.46.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)

  Downloading typing_inspection-0.4.2-py3-none-any.whl.metadata (2.6 kB)

  Downloading anyio-4.13.0-py3-none-any.whl.metadata (4.5 kB)

Collecting idna>=2.8 (from anyio<5,>=3.4.0->starlette<0.39.0,>=0.37.2->fastapi==0.115.0->-r requirements.txt (line 1))

  Downloading idna-3.11-py3-none-any.whl.metadata (8.4 kB)

Downloading fastapi-0.115.0-py3-none-any.whl (94 kB)

Downloading click-8.3.2-py3-none-any.whl (108 kB)

Downloading h11-0.16.0-py3-none-any.whl (37 kB)

Downloading httptools-0.7.1-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (517 kB)

Downloading pydantic-2.13.2-py3-none-any.whl (471 kB)

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.1/2.1 MB 212.7 MB/s eta 0:00:00
Downloading pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (807 kB)

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 807.9/807.9 kB 777.8 MB/s eta 0:00:00
Downloading typing_extensions-4.15.0-py3-none-any.whl (44 kB)

Downloading uvloop-0.22.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (4.4 MB)

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.4/4.4 MB 351.2 MB/s eta 0:00:00

Downloading annotated_types-0.7.0-py3-none-any.whl (13 kB)

Downloading typing_inspection-0.4.2-py3-none-any.whl (14 kB)

Installing collected packages: websockets, uvloop, typing-extensions, pyyaml, python-dotenv, idna, httptools, h11, click, annotated-types, uvicorn, typing-inspection, pydantic-core, anyio, watchfiles, starlette, pydantic, fastapi

Successfully installed annotated-types-0.7.0 anyio-4.13.0 click-8.3.2 fastapi-0.115.0 h11-0.16.0 httptools-0.7.1 idna-3.11 pydantic-2.13.2 pydantic-core-2.46.2 python-dotenv-1.2.2 pyyaml-6.0.3 starlette-0.38.6 typing-extensions-4.15.0 typing-inspection-0.4.2 uvicorn-0.30.0 uvloop-0.22.1 watchfiles-1.1.1 websockets-16.0

[stage-0 6/8] RUN --mount=type=cache,id=s/ff3b4317-d2ed-44f7-a79b-85549fe1fbb3-/root/cache/pip,target=/root/.cache/pip python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt
[stage-0 7/8] RUN printf '\nPATH=/opt/venv/bin:$PATH' >> /root/.profile
[stage-0 7/8] RUN printf '\nPATH=/opt/venv/bin:$PATH' >> /root/.profile
[stage-0 8/8] COPY . /app
[stage-0 8/8] COPY . /app
exporting to docker image format
exporting to docker image format
containerimage.digest: sha256:68191e923b8122a190d846c8909d18f31441f4c6448de2c9097918ac5ffd4b9a
containerimage.descriptor: eyJtZWRpYVR5cGUiOiJhcHBsaWNhdGlvbi92bmQub2NpLmltYWdlLm1hbmlmZXN0LnYxK2pzb24iLCJkaWdlc3QiOiJzaGEyNTY6NjgxOTFlOTIzYjgxMjJhMTkwZDg0NmM4OTA5ZDE4ZjMxNDQxZjRjNjQ0OGRlMmM5MDk3OTE4YWM1ZmZkNGI5YSIsInNpemUiOjIzODIsImFubm90YXRpb25zIjp7Im9yZy5vcGVuY29udGFpbmVycy5pbWFnZS5jcmVhdGVkIjoiMjAyNi0wNC0xN1QxNDoxMjowNloifSwicGxhdGZvcm0iOnsiYXJjaGl0ZWN0dXJlIjoiYW1kNjQiLCJvcyI6ImxpbnV4In19
containerimage.config.digest: sha256:5686b53f92a90d74387750c9cfbea73911edf00184b21159c2ef6ce65158cfc5
image push
Deploy complete
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
Starting Container
INFO:     100.64.0.2:35271 - "GET /health HTTP/1.1" 200 OK

====================
Starting Healthcheck
====================

Path: /health
Retry window: 30s

[1/1] Healthcheck succeeded!
INFO:     100.64.0.3:38522 - "GET / HTTP/1.1" 200 OK
INFO:     100.64.0.4:36804 - "GET /favicon.ico HTTP/1.1" 404 Not Found
INFO:     100.64.0.3:40772 - "GET /healthj HTTP/1.1" 404 Not Found
INFO:     100.64.0.4:32078 - "GET /health HTTP/1.1" 200 OK
INFO:     100.64.0.5:34818 - "GET / HTTP/1.1" 200 OK
INFO:     100.64.0.6:47800 - "GET /docs HTTP/1.1" 200 OK
INFO:     100.64.0.7:42824 - "GET /openapi.json HTTP/1.1" 200 OK
INFO:     100.64.0.5:51814 - "GET / HTTP/1.1" 200 OK
```