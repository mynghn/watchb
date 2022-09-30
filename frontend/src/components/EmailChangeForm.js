import { useState } from "react";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";

import FormInput from "./FormInput";

import store from "../store";
import { checkEmailPatternAndRedundancy } from "../utils/validators";
import { changeEmail } from "../api";

export default function EmailChangeForm({ onSuccess }) {
  const [isPwdRejected, setIsPwdRejected] = useState(null);
  const {
    auth: {
      user: { email },
    },
  } = store.getState();

  const checkEmailDiff = (newEmail) => ({
    isValid: newEmail !== email,
    message: newEmail !== email ? "" : "새로운 이메일 주소를 입력해주세요.",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const isValid = form.checkValidity();
    if (isValid) {
      const { newEmail, currPwd } = form;
      changeEmail(newEmail.value, currPwd.value)
        .then(onSuccess)
        .catch(
          ({
            response: {
              data: { curr_password: pwdErrMsg },
            },
          }) => {
            console.log(pwdErrMsg);
            if (
              pwdErrMsg[0].startsWith("Please request with correct password")
            ) {
              setIsPwdRejected(true);
            }
          }
        );
    }
  };

  return (
    <Form noValidate onSubmit={handleSubmit}>
      <Form.Group>
        <Form.Label>기존 이메일 주소</Form.Label>
        <FormInput plaintext readOnly defaultValue={email} />
      </Form.Group>
      <Form.Group>
        <Form.Label>새 이메일 주소</Form.Label>
        <FormInput
          name="newEmail"
          type="email"
          required
          validators={[checkEmailDiff, checkEmailPatternAndRedundancy]}
          defaultMessages={{ invalid: "정확하지 않은 이메일입니다." }}
        />
      </Form.Group>
      <Form.Group>
        <Form.Label>비밀번호</Form.Label>
        <Form.Control
          name="currPwd"
          type="password"
          required
          isInvalid={isPwdRejected}
          onChange={() => {
            if (isPwdRejected) {
              setIsPwdRejected(false);
            }
          }}
        />
        <Form.Control.Feedback type="invalid" style={{ textAlign: "start" }}>
          비밀번호가 일치하지 않습니다.
        </Form.Control.Feedback>
      </Form.Group>
      <Button type="submit">변경하기</Button>
    </Form>
  );
}
