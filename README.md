# website-uptime-tracker

Simple example uptime tracker that collects website uptime statistics
with Aiven DBaaS components.

## How to set up the development environment

The [Makefile](./Makefile) has rules for setting (almost) everything up
for you.

Prerequisites:
 1. Install Python3 (and jq and sed, the Makefile rules use those).
 2. Create an account in Aiven (unless you have already) and set up
    password authentication (because Aiven CLI doesn't work with social
    login).

After this, you can run the tests with `make`.  It also asks you to log
in and creates the background services in Aiven.  You can change the
names at the beginning of the Makefile.

If you want to skip some step of the setup, you can mark it as already
done by running e.g. `touch stamps/aiven-login`.  If you only want to
set it up to a given point, you can run that target, e.g. `make
stamps/install-deps`.

If you are editing the source, you might want to run the tests whenever
a source file changes.  You can do this by `make run-test-runner`.

## How to run the service manually

Fire up two shells.  In one, run the queue producer:

```
./myenv/bin/python uptime_producer.py <url-to-watch> --kafka-host <kafka-host>
```

... and in the other, the consumer:

```
$ ./myenv/bin/python uptime_consumer.py <kafka-host> <pg-url>
```

Also, you might want to get an SQL console to the uptime database:

```
$ psql <pg-url>
```

Here, <kafka-host> is the bootstrap server for connecting to Kafka; the
setup process above saves it in `kafka.host` so you can check from
there, but you can also get it from the Aiven console.

<url-to-watch> is the web page/service you want to generate uptime
statistics for.  It can be any URL; nonexistent pages will cause error
statuses.

<pg-url> is a connection URL for the PostgreSQL database where the
records are to be persisted.  You can get it from the Aiven console.

