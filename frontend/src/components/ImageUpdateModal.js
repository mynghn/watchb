import { useState } from "react";
import { useSelector } from "react-redux";

import Modal from "react-bootstrap/Modal";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";

import WarningModal from "./WarningModal";

export default function ImageUpdateModal({
  imgType,
  updateFn,
  deleteFn,
  actionNm = "",
  header = "",
  ...modalProps
}) {
  const [show, setShow] = useState(false);
  const [file, setFile] = useState(null);
  const user = useSelector(({ auth: { user } }) => user);

  const handleChange = (e) => {
    const {
      currentTarget: { files },
    } = e;
    if (files.length > 0) setFile(files[0]);
    else setFile(null);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append(imgType, file);

    updateFn(formData).then(setShow(false));
  };

  return (
    <>
      <div onClick={() => setShow(true)} style={{ cursor: "pointer" }}>
        {actionNm}
      </div>

      <Modal show={show} onHide={() => setShow(false)} {...modalProps}>
        <Modal.Header closeButton>{header}</Modal.Header>
        {user[imgType] ? (
          <Modal.Body>
            <WarningModal
              callbackFn={deleteFn}
              actionNm="현재 사진 삭제"
              warningMsg="삭제하시겠어요?"
              centered
            />
          </Modal.Body>
        ) : null}
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group>
              <Form.Label>사진 업로드</Form.Label>
              <Form.Control
                type="file"
                accept="image/jpeg,image/png"
                onChange={handleChange}
              />
            </Form.Group>
            <Button type="submit" disabled={!file}>
              확인
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </>
  );
}
