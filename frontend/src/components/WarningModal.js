import { useState } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

export default function WarningModal({
  callbackFn,
  title = "",
  actionNm = "",
  warningMsg = "",
  ...modalProps
}) {
  const [show, setShow] = useState(false);
  return (
    <>
      <div onClick={() => setShow(true)} style={{ cursor: "pointer" }}>
        {actionNm}
      </div>
      <Modal show={show} onHide={() => setShow(false)} {...modalProps}>
        <Modal.Title>{title}</Modal.Title>
        <Modal.Body>{warningMsg}</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShow(false)}>
            취소
          </Button>
          <Button variant="danger" onClick={callbackFn}>
            확인
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
