import { useEffect, useRef } from "react";

export default function useEffectOnUpdates(effect, deps) {
  const didMount = useRef(false);
  useEffect(() => {
    if (didMount.current) return effect();
    else didMount.current = true;
    /* eslint-disable react-hooks/exhaustive-deps*/
  }, [...deps]);
}
