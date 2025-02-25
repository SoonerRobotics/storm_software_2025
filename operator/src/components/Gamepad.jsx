import React, { useContext, useEffect, useRef, useState } from "react";
import interval from "../hooks/interval";
import { GamepadsContext } from "../context/GamepadContext";

export default function GamepadController() {
  const [ gamepads, setGamepads ] = useState({});
  const requestRef = useRef();
  const { gamepads: globalGamepads, updateGlobalGamepads } = useContext(
    GamepadsContext
  );
  var haveEvents = "ongamepadconnected" in window;

  const addGamepad = gamepad => {
    updateGlobalGamepads({
      ...gamepads,
      [gamepad.index]: {
        buttons: gamepad.buttons,
        id: gamepad.id,
        axes: gamepad.axes
      }
    });
    setGamepads({
      ...gamepads,
      [gamepad.index]: {
        buttons: gamepad.buttons,
        id: gamepad.id,
        axes: gamepad.axes
      }
    });

  };

  const connectGamepadHandler = e => {
    addGamepad(e.gamepad);
  };

  const scanGamepads = () => {
    var detectedGamepads = navigator.getGamepads
      ? navigator.getGamepads()
      : navigator.webkitGetGamepads
      ? navigator.webkitGetGamepads()
      : [];

    for (var i = 0; i < detectedGamepads.length; i++) {
      if (detectedGamepads[i]) {
        addGamepad(detectedGamepads[i]);
      }
    }
  };

  useEffect(() => {
    window.addEventListener("gamepadconnected", connectGamepadHandler);

    return window.removeEventListener(
      "gamepadconnected",
      connectGamepadHandler
    );
  });

  const animate = time => {
    if (!haveEvents) scanGamepads();
    requestRef.current = requestAnimationFrame(animate);
  };

  useEffect(() => {
    requestRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(requestRef.current);
  });

  useInterval(() => {
    if (!haveEvents) scanGamepads();
  }, 1000);

  const gamepadDisplay = Object.keys(globalGamepads).map(gamepadId => {
    return (
      <div>
        <h2>{globalGamepads[gamepadId].id}</h2>
        {globalGamepads[gamepadId].buttons &&
          globalGamepads[gamepadId].buttons.map((button, index) => (
            <div>
              {index}: {button.pressed ? "True" : "False"}
            </div>
          ))}
      </div>
    );
  });

  return (
    <div className="Gamepads">
      <h1>Gamepads</h1>
      {gamepadDisplay}
    </div>
  );

}
