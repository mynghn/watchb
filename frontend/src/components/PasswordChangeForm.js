import { useState } from "react";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";

import FormInput from "./FormInput";

import { checkPasswordPattern } from "../utils/validators";
import { changePassword } from "../api";

const CURR_PWD_LABEL = "기존 비밀번호";
const CURR_PWD_INPUT_ID = "currPwd";
const CURR_PWD_REJECTED_MSG = "비밀번호가 틀립니다.";

const NEW_PWD_LABEL = "새 비밀번호";
const NEW_PWD_INPUT_ID = "newPwd";
const NEW_PWD_SHORT_MSG = "비밀번호는 최소 8자리 이상이어야 합니다.";
const NEW_PWD_NOT_NEW_MSG = "새로운 비밀번호를 입력해주세요.";

const REWRITE_NEW_PWD_LABEL = "새 비밀번호 재입력";
const REWRITE_PWD_NOT_SAME_MSG = "비밀번호가 일치하지 않습니다.";
const WRONG_PWD_API_ERR_MSG = "Please request with correct password";

export default function PasswordChangeForm({ onSuccess }) {
  const [isPwdRejected, setIsPwdRejected] = useState(null);
  const [newPwd, setNewPwd] = useState("");
  const [currPwd, setCurrPwd] = useState("");

  const checkNew = (newPwd) => {
    const isNew = newPwd !== currPwd;
    return {
      isValid: isNew,
      message: isNew ? "" : NEW_PWD_NOT_NEW_MSG,
    };
  };
  const checkRewrite = (newPwdRewrite) => {
    const isSame = newPwdRewrite === newPwd;
    return {
      isValid: isSame,
      message: isSame ? "" : REWRITE_PWD_NOT_SAME_MSG,
    };
  };

  const handleCurrPwdChange = (e) => {
    if (isPwdRejected) {
      setIsPwdRejected(false);
    }
    setCurrPwd(e.currentTarget.value);
  };
  const handleNewPwdChange = (e) => {
    setNewPwd(e.currentTarget.value);
  };
  const onChangePasswordError = ({
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
      const { newPwd, currPwd } = form;
      changePassword(newPwd.value, currPwd.value)
        .then(onSuccess)
        .catch(onChangePasswordError);
    }
  };

  return (
    <Form noValidate onSubmit={handleSubmit}>
      <Form.Group>
        <Form.Label>{CURR_PWD_LABEL}</Form.Label>
        <Form.Control
          id={CURR_PWD_INPUT_ID}
          type="password"
          required
          isInvalid={isPwdRejected}
          onChange={handleCurrPwdChange}
        />
        <Form.Control.Feedback type="invalid" style={{ textAlign: "start" }}>
          {CURR_PWD_REJECTED_MSG}
        </Form.Control.Feedback>
      </Form.Group>
      <Form.Group>
        <Form.Label>{NEW_PWD_LABEL}</Form.Label>
        <FormInput
          id={NEW_PWD_INPUT_ID}
          type="password"
          required
          minLength={8}
          maxLength={20}
          validators={[checkPasswordPattern, checkNew]}
          defaultMessages={{ invalid: NEW_PWD_SHORT_MSG }}
          onChange={handleNewPwdChange}
        />
      </Form.Group>
      <Form.Group>
        <Form.Label>{REWRITE_NEW_PWD_LABEL}</Form.Label>
        <FormInput type="password" required validators={[checkRewrite]} />
      </Form.Group>
      <Button type="submit">변경하기</Button>
    </Form>
  );
}
