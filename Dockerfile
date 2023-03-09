FROM codinuum/cca:devel-20.04

LABEL maintainer="mstmhsmt"

ARG USER=user
ARG GROUP=user
ARG UID=1001
ARG GID=1001

RUN set -x && \
    groupadd -g $GID $GROUP && \
    useradd -u $UID -g $GID -m -s /bin/bash $USER

RUN set -x && \
    cd /root && \
    apt-get update && \
    env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        time

RUN set -x && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /home/$USER/
USER $USER

COPY --chown=$USER:$GROUP configs configs/
COPY --chown=$USER:$GROUP projects projects/
COPY --chown=$USER:$GROUP README.md mkdistmat.py mkdistmat.sh .

RUN set -x && \
    echo 'export PATH=/opt/cca/bin:${PATH}' >> .bashrc

CMD ["/bin/bash"]

