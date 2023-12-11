FROM ubergarm/l2tp-ipsec-vpn-client

RUN mkdir -p /root/.ssh \
    && chmod 0700 /root/.ssh \
    && apk add openrc openssh curl

RUN sed -i 's/#Port 22/Port 222/' /etc/ssh/sshd_config
RUN sed -i 's/ike=3des-sha1;modp1024/ike=aes128-sha2_256;modp1536/' /etc/ipsec.conf


RUN touch  /entrypoint.sh \
    && echo "#!/bin/sh" > /entrypoint.sh \
    && echo "modprobe af_key" >> /entrypoint.sh \
    && echo "modprobe l2tp_ppp" >> /entrypoint.sh \
    && echo "ssh-keygen -A" >> /entrypoint.sh \
    && echo 'exec /usr/sbin/sshd -D -e "$@"' >> /entrypoint.sh \
    && chmod +x /entrypoint.sh

EXPOSE 222
ENTRYPOINT ["sh", "/entrypoint.sh"]