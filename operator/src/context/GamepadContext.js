import React, { createContext, useEffect, useRef, useState } from "react";
import interval from "../hooks/interval";

const GamepadsContext = createContext();

const GamepadsProvider = ({ children }) => {
  const [gamepads, setGamepads] = useState();
  const requestRef = useRef();
  var haveEvents = "ongamepadconnected" in window;

  const addGamepad = (gamepad) => {
    setGamepads({
      ...gamepads,
      [gamepad.index]: {
        buttons: gamepad.buttons,
        id: gamepad.id,
        axes: gamepad.axes
      }
    });
  };

  const connectGamepadhandler = (e) => {
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

  const animate = (time) => {
    if (!haveEvents) scanGamepads();
    requestRef.current = requestAnimationFrame(animate);
  };

  useEffect(() => {
    requestRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(requestRef.current);
  }, []);

  interval(() => {
    if (!haveEvents) scanGamepads();
  }, 1000);

  return (
    <GamepadsContext.Provider value={{ gamepads, setGamepads }}>
      {children}
    </GamepadsContext.Provider>
  );
};

export { GamepadsProvider, GamepadsContext };


}
