import { useState } from "react";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import Modal from "react-bootstrap/Modal";
import { Link } from "react-router-dom";

import BrandLogo from "./BrandLogo";
import FormInput from "./FormInput";
import SignUpModal from "./SignUpModal";

import { obtainJWT, retrieveUser } from "../api";
import { useDispatch } from "react-redux";
import { setUser, login as reduxLogin } from "../store";

const EMAIL_PROPS = {
  type: "email",
  name: "emailInput",
  placeholder: "이메일",
  autoFocus: true,
  required: true,
};
const EMAIL_INVALID_MESSAGE = "정확하지 않은 이메일입니다.";

const PASSWORD_PROPS = {
  type: "password",
  name: "passwordInput",
  placeholder: "비밀번호",
  required: true,
  minLength: 8,
  maxLength: 20,
};
const PASSWORD_INVALID_MESSAGE = "비밀번호는 최소 8자리 이상이어야 합니다.";

export default function LoginModal() {
  const [show, setShow] = useState(false);
  const [isValidated, setisValidated] = useState(false);

  const dispatch = useDispatch();

  const login = (email, password) => {
    obtainJWT(email, password)
      .then(retrieveUser)
      .then(({ data: { id: userId, username } }) => {
        dispatch(setUser({ userId, username }));
        dispatch(reduxLogin());
      });
  };
  const handleSubmit = (e) => {
    e.preventDefault();

    const form = e.currentTarget;
    const isValid = form.checkValidity();
    setisValidated(true);

    if (isValid) {
      const { emailInput, passwordInput } = form;
      login(emailInput.value, passwordInput.value);
    }
  };

  return (
    <>
      <Button onClick={() => setShow(true)}>로그인</Button>

      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header
          style={{
            border: "none",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <BrandLogo />
          <Modal.Title>로그인</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ textAlign: "center" }}>
          <Form noValidate validated={isValidated} onSubmit={handleSubmit}>
            <FormInput
              defaultMessages={{ invalid: EMAIL_INVALID_MESSAGE }}
              {...EMAIL_PROPS}
            />
            <FormInput
              defaultMessages={{ invalid: PASSWORD_INVALID_MESSAGE }}
              {...PASSWORD_PROPS}
            />
            <Button type="submit">로그인</Button>
          </Form>
          <Link to="">비밀번호를 잊어버리셨나요?</Link>
          <div>
            계정이 없으신가요? <SignUpModal />
          </div>
        </Modal.Body>
        <Modal.Footer style={{ justifyContent: "center" }}>
          소셜 로그인
        </Modal.Footer>
      </Modal>
    </>
  );
}
