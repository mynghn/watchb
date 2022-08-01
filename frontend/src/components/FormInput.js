import { useEffect, useState } from "react";
import Form from "react-bootstrap/Form";

export default function FormInput({
  validators,
  validMessage,
  invalidMessage,
  ...htmlInputProps
}) {
  const [hasBlurred, setHasBlurred] = useState(false);

  const [isValid, setIsValid] = useState();
  const [showValid, setShowValid] = useState(false);
  const [showInvalid, setShowInvalid] = useState(false);
  const displayValidity = () => {
    setShowValid(isValid);
    if (hasBlurred) {
      setShowInvalid(!isValid);
    }
  };
  useEffect(displayValidity, [isValid, hasBlurred]);

  const checkValidity = async (inputDOM) => {
    let validity = inputDOM.checkValidity();

    // extra validity check with custom validators
    if (validity && Array.isArray(validators)) {
      // filter out non-functions
      const validatorFns = validators.filter(
        (validator) => typeof validator === "function"
      );
      // check extra validities with ANDs
      let extraValidity = true;
      for (let idx = 0; idx < validatorFns.length; idx++) {
        extraValidity &&= await validatorFns[idx](inputDOM.value);
        if (!extraValidity) {
          break;
        }
      }
      validity = validity && extraValidity;
    }

    return validity;
  };

  const handleChange = async (e) => {
    const currValidity = await checkValidity(e.currentTarget);
    setIsValid(currValidity);
  };
  const handleBlur = () => {
    if (!hasBlurred) setHasBlurred(true);
  };

  return (
    <Form.Group>
      <Form.Control
        isValid={showValid}
        isInvalid={showInvalid}
        onChange={handleChange}
        onBlur={handleBlur}
        {...htmlInputProps}
      />
      <Form.Control.Feedback type="valid" style={{ textAlign: "start" }}>
        {validMessage}
      </Form.Control.Feedback>
      <Form.Control.Feedback type="invalid" style={{ textAlign: "start" }}>
        {invalidMessage}
      </Form.Control.Feedback>
    </Form.Group>
  );
}
