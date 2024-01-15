import winston from "winston"
import cron from "node-cron"
import { execSync } from 'child_process';
import Docker from "dockerode"

const docker = new Docker();
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
    transports: [
        new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/combined.log' }),
    ],
});

if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
        format: winston.format.simple(),
    }));
}

async function executeCommand(container, cmd) {
    const exec = await container.exec({
        Cmd: cmd,
        AttachStdout: true,
        AttachStderr: true,
    });
    const stream = await exec.start({});
    const finish = new Promise((resolve) => {
        // stream.on("end", resolve)
        // workaround
        const timer = setInterval(async () => {
            const r = await exec.inspect();
            if (!r.Running) {
                clearInterval(timer);
                stream.destroy();
                resolve();
            }
        }, 1e3);
    });
    docker.modem.demuxStream(stream, process.stdout, process.stderr);
    await finish
}

async function update() {
    logger.info("Started update")

    const containerName = 'screepsloan-loan-1'

    const container = docker.getContainer(containerName);
    const commands = [
        ['flask', 'import-users'],
        ['flask', 'import-rankings'],
        ['flask', 'import-user-rankings']
    ]
    for (let i = 0; i < commands.length; i++) {
        const baseCommand = commands[i];
        const command = `docker exec ${containerName} ${baseCommand}`;
        try {
            const startTime = Date.now();
            logger.info(`Starting ${command}`)
            await executeCommand(container, baseCommand)

            const endTime = Date.now();
            const timeTakenMilliseconds = endTime - startTime;
            const timeTakenSeconds = Math.round(timeTakenMilliseconds / 1000);
            const timeTakenMinutes = Math.round(timeTakenSeconds / 60);

            logger.info(`Took ${timeTakenSeconds} seconds (${timeTakenMinutes} minutes)`);
        } catch (e) {
            logger.error(`Command: ${command}`)
            logger.error(e)
        }
    }

    logger.info("Finished update")
}

cron.schedule('0 */6 * * *', () => {
    update();
});