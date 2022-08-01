import { useEffect, useState } from "react";
import Form from "react-bootstrap/Form";

export default function FormInput({
  validators,
  defaultMessages = { valid: "", invalid: "" },
  ...htmlInputProps
}) {
  const [hasBlurred, setHasBlurred] = useState(false);

  const [validation, setValidation] = useState({ isValid: null, message: "" });
  const getDefaultMessage = (isValid) =>
    isValid ? defaultMessages.valid : defaultMessages.invalid;

  const [showValid, setShowValid] = useState(false);
  const [showInvalid, setShowInvalid] = useState(false);
  const displayValidation = () => {
    const { isValid } = validation;
    setShowValid(isValid);
    if (hasBlurred) {
      setShowInvalid(!isValid);
    }
  };
  useEffect(displayValidation, [validation, hasBlurred]);

  const checkValidity = async (inputDOM) => {
    let isValid = inputDOM.checkValidity();
    let message = getDefaultMessage(isValid);

    // extra validity check with custom validators
    if (isValid && Array.isArray(validators)) {
      // filter out non-functions
      const validatorFns = validators.filter(
        (validator) => typeof validator === "function"
      );
      // check extra validities with ANDs
      for (let idx = 0; idx < validatorFns.length; idx++) {
        const { isValid: isVld, message: msg } = await validatorFns[idx](
          inputDOM.value
        );
        // accumulate validation results
        isValid &&= isVld;
        message =
          msg && typeof msg === "string" ? msg : getDefaultMessage(isVld);
        // break when any validator fails
        if (!isValid) break;
      }
    }
    return { isValid, message };
  };

  const handleChange = async (e) => {
    setValidation(await checkValidity(e.currentTarget));
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
      <Form.Control.Feedback
        type={validation.isValid ? "valid" : "invalid"}
        style={{ textAlign: "start" }}
      >
        {validation.message}
      </Form.Control.Feedback>
    </Form.Group>
  );
}
