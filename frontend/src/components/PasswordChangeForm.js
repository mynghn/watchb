import { useState } from "react";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";

import FormInput from "./FormInput";

import { checkPasswordPattern } from "../utils/validators";
import { changePassword } from "../api";

const DEFAULT_PASSWORD_INVALID_MESSAGE =
  "비밀번호는 최소 8자리 이상이어야 합니다.";

export default function PasswordChangeForm({ onSuccess }) {
  const [isPwdRejected, setIsPwdRejected] = useState(null);
  const [newPwd, setNewPwd] = useState("");
  const [currPwd, setCurrPwd] = useState("");

  const checkPwdDiff = (newPwd) => ({
    isValid: newPwd !== currPwd,
    message: newPwd !== currPwd ? "" : "새로운 비밀번호를 입력해주세요.",
  });
  const checkPwdRewrite = (newPwdRewrite) => ({
    isValid: newPwdRewrite === newPwd,
    message: newPwdRewrite === newPwd ? "" : "비밀번호가 일치하지 않습니다.",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const isValid = form.checkValidity();
    if (isValid) {
      const { newPwd, currPwd } = form;
      changePassword(newPwd.value, currPwd.value)
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
        <Form.Label>기존 비밀번호</Form.Label>
        <Form.Control
          name="currPwd"
          type="password"
          required
          isInvalid={isPwdRejected}
          onChange={(e) => {
            if (isPwdRejected) {
              setIsPwdRejected(false);
            }
            setCurrPwd(e.currentTarget.value);
          }}
        />
        <Form.Control.Feedback type="invalid" style={{ textAlign: "start" }}>
          비밀번호가 틀립니다.
        </Form.Control.Feedback>
      </Form.Group>
      <Form.Group>
        <Form.Label>새 비밀번호</Form.Label>
        <FormInput
          name="newPwd"
          type="password"
          required
          minLength={8}
          maxLength={20}
          validators={[checkPasswordPattern, checkPwdDiff]}
          defaultMessages={{ invalid: DEFAULT_PASSWORD_INVALID_MESSAGE }}
          onChange={(e) => {
            setNewPwd(e.currentTarget.value);
          }}
        />
      </Form.Group>
      <Form.Group>
        <Form.Label>새 비밀번호 재입력</Form.Label>
        <FormInput type="password" required validators={[checkPwdRewrite]} />
      </Form.Group>
      <Button type="submit">변경하기</Button>
    </Form>
  );
}
