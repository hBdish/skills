package handlers

import "testing"

func TestValidateEmpty(t *testing.T) {
	h := newHandler(t)
	if h.Validate("") == nil {
		t.Error("failed")
	}
}

func TestValidateOk(t *testing.T) {
	h := newHandler(t)
	if h.Validate("u1") != nil {
		t.Error("failed")
	}
}

func TestSave(t *testing.T) {
	h := newHandler(t)
	err := h.Save(nil)
	if err.Error() != "Save incomplete!" {
		t.Errorf("wrong error")
	}
}

func TestSyncConcurrent(t *testing.T) {
	h := newHandler(t)
	done := make(chan bool)
	go func() {
		if err := h.store.Sync(h.ctx); err != nil {
			t.Fatal(err)
		}
		done <- true
	}()
	<-done
}

func newHandler(t *testing.T) *UserHandler {
	return &UserHandler{}
}
