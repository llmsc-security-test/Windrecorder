# =============================================================================
# Dockerfile – CentOS 7 with devtoolset‑7 and Python 3 (via SCL)
# Updated to work reliably with the vault repositories and to install a
# functional Python 3 interpreter.
# =============================================================================
FROM centos:7

LABEL author="Pad0y <github.com/Pad0y>"

# ----------------------------------------------------------------------
# 1. Point all CentOS repo URLs to the vault (EOL) mirrors.
# 2. Install yum‑utils, EPEL and the SCL release packages.
# 3. Apply the vault fix to the newly added repo files.
# 4. Install devtoolset‑7 and the Python 3 SCL (rh‑python38).
# 5. Install the required build/runtime libraries.
# 6. Clean up yum caches.
# ----------------------------------------------------------------------
RUN set -eux; \
    \
    # ---- 1. Redirect CentOS repos to vault.centos.org --------------------
    sed -i -e 's|^mirrorlist=|#mirrorlist=|g' \
           -e 's|^#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' \
           -e 's|^baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' \
           -e 's|mirror.centos.org|vault.centos.org|g' \
           /etc/yum.repos.d/*.repo; \
    \
    # ---- 2. Make yum a little more tolerant -----------------------------
    yum -y install yum-utils; \
    yum-config-manager --save --setopt=*.timeout=300; \
    yum-config-manager --save --setopt=*.retries=5; \
    \
    # ---- 3. Install EPEL and SCL release packages -----------------------
    yum -y install epel-release centos-release-scl centos-release-scl-rh; \
    \
    # ---- 4. Re‑apply the vault fix to the newly added repo files -------
    sed -i -e 's|^mirrorlist=|#mirrorlist=|g' \
           -e 's|^#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' \
           -e 's|^baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' \
           -e 's|mirror.centos.org|vault.centos.org|g' \
           /etc/yum.repos.d/*.repo; \
    \
    # ---- 5. Install devtoolset‑7 and Python 3 SCL ------------------------
    yum -y install devtoolset-7 rh-python38 rh-python38-python-pip rh-python38-python-devel; \
    \
    # ---- 6. Install other build/runtime dependencies --------------------
    # Development Tools group (compilers, make, etc.)
    yum -y groupinstall "Development Tools"; \
    # Additional libraries required by the application
    yum -y install \
        git wget \
        libSM-devel libXrender-devel libXext-devel \
        zlib-devel bzip2-devel openssl-devel ncurses-devel \
        sqlite-devel readline-devel tk-devel gdbm-devel \
        libpcap-devel xz-devel libffi-devel; \
    \
    # ---- 7. Clean up ----------------------------------------------------
    yum clean all && rm -rf /var/cache/yum

# ----------------------------------------------------------------------
# Enable devtoolset‑7 and rh-python38 for all subsequent RUN / CMD / ENTRYPOINT steps
# ----------------------------------------------------------------------
ENV BASH_ENV="/opt/rh/devtoolset-7/enable:/opt/rh/rh-python38/enable"
ENV ENV="/opt/rh/devtoolset-7/enable:/opt/rh/rh-python38/enable"
ENV PATH="/opt/rh/devtoolset-7/root/usr/bin:/opt/rh/devtoolset-7/root/usr/sbin:/opt/rh/rh-python38/root/usr/bin:${PATH}"

# ----------------------------------------------------------------------
# Upgrade pip (the one from rh-python38) and point it at fast mirrors
# ----------------------------------------------------------------------
RUN pip3 install --no-cache-dir -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# ----------------------------------------------------------------------
# Copy source, install Python requirements
# ----------------------------------------------------------------------
COPY . /data/project/
WORKDIR /data/project/

RUN pip3 install --no-cache-dir -r requirements.txt

# ----------------------------------------------------------------------
# Expose ports & entrypoint
# ----------------------------------------------------------------------
EXPOSE 5000 8000 8501

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    mkdir -p /var/log && touch /var/log/app.log

ENTRYPOINT ["/entrypoint.sh"]