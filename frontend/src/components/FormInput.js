import { useState } from "react";
import Form from "react-bootstrap/Form";

export default function FormInput({
  validationFunc,
  validMessage,
  invalidMessage,
  ...htmlInputProps
}) {
  const [hasBlurred, setHasBlurred] = useState(false);

  const [isValid, setIsValid] = useState();
  const [isInvalid, setIsinValid] = useState();
  const setValidity = (validity) => {
    setIsValid(validity);
    setIsinValid(!validity);
  };

  const checkValidity = (inputDOM) => {
    let validity = inputDOM.checkValidity();
    if (typeof validationFunc === "function") {
      validity = validity && validationFunc(inputDOM.value);
    }
    return validity;
  };

  const handleChange = (e) => {
    if (hasBlurred) {
      setValidity(checkValidity(e.currentTarget));
    }
  };
  const handleBlur = (e) => {
    if (!hasBlurred) {
      setHasBlurred(true);
      setValidity(checkValidity(e.currentTarget));
    }
  };

  return (
    <Form.Group>
      <Form.Control
        isValid={isValid}
        isInvalid={isInvalid}
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
