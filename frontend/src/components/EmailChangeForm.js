import { useState } from "react";
import { useSelector } from "react-redux";

import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";

import FormInput from "./FormInput";

import { checkEmailPatternAndRedundancy } from "../utils/validators";
import { changeEmail } from "../api";

const CURR_EMAIL_LABEL = "기존 이메일 주소";

const NEW_EMAIL_LABEL = "새 이메일 주소";
const NEW_EMAIL_INPUT_ID = "newEmail";
const NEW_EMAIL_INVALID_MSG = "정확하지 않은 이메일입니다.";
const NEW_EMAIL_NOT_NEW_MSG = "정확하지 않은 이메일입니다.";

const PWD_LABEL = "비밀번호";
const PWD_INPUT_ID = "currPwd";
const WRONG_PWD_API_ERR_MSG = "Please request with correct password";
const PWD_REJECTED_MSG = "비밀번호가 일치하지 않습니다.";

export default function EmailChangeForm({ onSuccess }) {
  const [isPwdRejected, setIsPwdRejected] = useState(null);
  const email = useSelector(
    ({
      auth: {
        user: { email },
      },
    }) => email
  );

  const checkNew = (newEmail) => {
    const isNew = newEmail !== email;
    return {
      isValid: isNew,
      message: isNew ? "" : NEW_EMAIL_NOT_NEW_MSG,
    };
  };

  const handlePwdChange = () => {
    if (isPwdRejected) {
      setIsPwdRejected(false);
    }
  };
  const onChangeEmailError = ({
    response: {
      data: { curr_password: pwdErrMsgs },
    },
  }) => {
    if (pwdErrMsgs.includes(WRONG_PWD_API_ERR_MSG)) {
      setIsPwdRejected(true);
    }
  };
  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const isValid = form.checkValidity();
    if (isValid) {
      changeEmail(form[NEW_EMAIL_INPUT_ID].value, form[PWD_INPUT_ID].value)
        .then(onSuccess)
        .catch(onChangeEmailError);
    }
  };

  return (
    <Form noValidate onSubmit={handleSubmit}>
      <Form.Group>
        <Form.Label>{CURR_EMAIL_LABEL}</Form.Label>
        <FormInput plaintext readOnly defaultValue={email} />
      </Form.Group>
      <Form.Group>
        <Form.Label>{NEW_EMAIL_LABEL}</Form.Label>
        <FormInput
          id={NEW_EMAIL_INPUT_ID}
          type="email"
          required
          validators={[checkNew, checkEmailPatternAndRedundancy]}
          defaultMessages={{ invalid: NEW_EMAIL_INVALID_MSG }}
        />
      </Form.Group>
      <Form.Group>
        <Form.Label>{PWD_LABEL}</Form.Label>
        <Form.Control
          id={PWD_INPUT_ID}
          type="password"
          required
          isInvalid={isPwdRejected}
          onChange={handlePwdChange}
        />
        <Form.Control.Feedback type="invalid" style={{ textAlign: "start" }}>
          {PWD_REJECTED_MSG}
        </Form.Control.Feedback>
      </Form.Group>
      <Button type="submit">변경하기</Button>
    </Form>
  );
}
