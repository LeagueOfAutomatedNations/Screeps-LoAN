var ScreepsRegion = (function () {
    function ScreepsRegion(topLeft, bottomRight) {
        this.topLeft = topLeft;
        this.bottomRight = bottomRight;
    }

    ScreepsRegion.prototype.getRect = function () {
        let topLeftRoom = this.getRoomRect(this.topLeft);
        let bottomRightRoom = this.getRoomRect(this.bottomRight);
        return {
            top: topLeftRoom.top,
            left: topLeftRoom.left,
            bottom: bottomRightRoom.bottom,
            right: bottomRightRoom.right
        };
    }

    ScreepsRegion.prototype.getRoomRect = function (name) {
        let xy = this.roomNameToXY(name);
        return {
            top: xy.y * ScreepsConstants.RoomSize,
            left: xy.x * ScreepsConstants.RoomSize,
            bottom: (xy.y + 1) * ScreepsConstants.RoomSize,
            right: (xy.x + 1) * ScreepsConstants.RoomSize
        };
    }

    ScreepsRegion.prototype.roomNameToXY = function (name) {
        let parts = name.match(/([EW])([0-9]*)([NS])([0-9]*)/);
        let x = parseInt(parts[2]);
        if (parts[1] == "W") {
            x = ~x;
        }
        let y = parseInt(parts[4]);
        if (parts[3] == "N") {
            y = ~y;
        }
        return { "x": x, "y": y };
    }

    ScreepsRegion.prototype.xyToRoomName = function (rx, ry) {
        let result = "";
        result += (rx < 0 ? "W" + String(~rx) : "E" + String(rx));
        result += (ry < 0 ? "N" + String(~ry) : "S" + String(ry));
        return result;
    }

    ScreepsRegion.prototype.worldPositionToXY = function (wx, wy) {
        return { x: Math.floor(wx / ScreepsConstants.RoomSize), y: Math.floor(wy / ScreepsConstants.RoomSize) };
    }

    ScreepsRegion.prototype.worldPositionToRoomName = function (wx, wy) {
        let xy = this.worldPositionToXY(wx, wy);

        return this.xyToRoomName(xy.x, xy.y);
    }

    ScreepsRegion.prototype.worldPositionInBounds = function (wx, wy) {
        let rect = this.getRect();
        return rect.left <= wx && wx <= rect.right &&
            rect.top <= wy && wy <= rect.bottom;
    }

    return ScreepsRegion;
}());
