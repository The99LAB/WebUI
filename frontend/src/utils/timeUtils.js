export function convertEpochToUptime(epochTime) {
    const upSince = new Date(epochTime * 1000);
    const currentTime = new Date();
    let timeDiff = currentTime - upSince;

    const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    timeDiff -= days * (1000 * 60 * 60 * 24);

    const hours = Math.floor(timeDiff / (1000 * 60 * 60));
    timeDiff -= hours * (1000 * 60 * 60);

    const minutes = Math.floor(timeDiff / (1000 * 60));
    timeDiff -= minutes * (1000 * 60);

    const seconds = Math.floor(timeDiff / 1000);

    // If days, hours, minutes or seconds are 0, don't display them.
    // The output should be formatted like this:
    // 2d 3h 4m 5s

    if (days > 0) {
        return `${days}d ${hours}h ${minutes}m ${seconds}s`;
    }
    if (hours > 0) {
        return `${hours}h ${minutes}m ${seconds}s`;
    }
    if (minutes > 0) {
        return `${minutes}m ${seconds}s`;
    }
    return `${seconds}s`;
}