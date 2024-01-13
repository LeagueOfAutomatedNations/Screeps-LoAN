import winston from "winston"
import cron from "node-cron"
import { execSync } from 'child_process';

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

async function update() {
    logger.info("Started update")

    const containerName = 'screepsloan-loan-1'
    const commands = [
        'flask import-users',
        'flask import-rankings',
        'flask import-alliances',
        'flask import-user-rankings'
    ]
    for (let i = 0; i < commands.length; i++) {
        const baseCommand = commands[i];
        const command = `docker exec ${containerName} ${baseCommand}`;
        try {
            const startTime = Date.now();
            logger.info(`Starting ${command}`)
            execSync(command, { encoding: 'utf-8' });

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