import { useState } from "react";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import Modal from "react-bootstrap/Modal";

import { signUp } from "../api";

import BrandLogo from "./BrandLogo";
import LoginModal from "./LoginModal";
import FormInput from "./FormInput";

const NAME_PROPS = {
  type: "text",
  name: "username",
  placeholder: "이름",
  autoFocus: true,
  required: true,
  minLength: 2,
  maxLength: 20,
};
const NAME_INVALID_MESSAGE = "정확하지 않은 이름입니다.";

const EMAIL_PROPS = {
  type: "email",
  name: "email",
  placeholder: "이메일",
  required: true,
};
const EMAIL_INVALID_MESSAGE = "정확하지 않은 이메일입니다.";

const PASSWORD_PROPS = {
  type: "password",
  name: "password",
  placeholder: "비밀번호",
  required: true,
  minLength: 8,
  maxLength: 20,
};
const PASSWORD_INVALID_MESSAGE =
  "비밀번호는 영문, 숫자, 특수문자 중 2개 이상을 조합하여 최소 8자리 이상이어야 합니다.";
const passwordValidation = (value) => {
  const en = /[a-z]/i;
  const num = /\d/;
  const spcialChar = /[^a-z\d]/i;
  return en.test(value) + num.test(value) + spcialChar.test(value) >= 2;
};

export default function SignUpModal() {
  const [show, setShow] = useState(false);
  const [isValidated, setisValidated] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const form = e.currentTarget;
    const isValid = form.checkValidity();
    setisValidated(true);

    if (isValid) {
      const { username, email, password } = form;

      await signUp(username.value, email.value, password.value);
    }
  };

  return (
    <>
      <Button onClick={() => setShow(true)}>회원가입</Button>

      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header
          style={{
            border: "none",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <BrandLogo />
          <Modal.Title>회원가입</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ textAlign: "center" }}>
          <Form noValidate validated={isValidated} onSubmit={handleSubmit}>
            <FormInput invalidMessage={NAME_INVALID_MESSAGE} {...NAME_PROPS} />
            <FormInput
              invalidMessage={EMAIL_INVALID_MESSAGE}
              {...EMAIL_PROPS}
            />
            <FormInput
              validationFunc={passwordValidation}
              invalidMessage={PASSWORD_INVALID_MESSAGE}
              {...PASSWORD_PROPS}
            />
            <Button type="submit">회원가입</Button>
          </Form>
          <div>
            이미 가입하셨나요? <LoginModal />
          </div>
        </Modal.Body>
        <Modal.Footer style={{ justifyContent: "center" }}>
          소셜 로그인
        </Modal.Footer>
      </Modal>
    </>
  );
}
