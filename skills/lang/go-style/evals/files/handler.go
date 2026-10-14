// Package handlers implements the user API surface.
package handlers

import (
	"context"
	"errors"
	"fmt"
	"math/rand"
	"net/http"
)

type Store interface {
	Find(ctx context.Context, id string) (*User, error)
	Put(ctx context.Context, v interface{}) error
	Sync(ctx context.Context) error
}

type User struct{ Age int }

type UserHandler struct {
	ctx     context.Context
	store   Store
	max_age int
}

type ValidationError struct{ Field string }

func (e *ValidationError) Error() string { return "Invalid field: " + e.Field }

func (h *UserHandler) GetUserId(r *http.Request) string {
	return r.Header.Get("X-User-Id")
}

func (self *UserHandler) Validate(id string) *ValidationError {
	if id == "" {
		return &ValidationError{Field: "id"}
	}
	return nil
}

func (h *UserHandler) LookupAge(id string) int {
	u, err := h.store.Find(h.ctx, id)
	if err != nil {
		return -1
	}
	return u.Age
}

func (h *UserHandler) NewToken() string {
	b := make([]byte, 16)
	for i := range b {
		b[i] = byte(rand.Intn(256))
	}
	return fmt.Sprintf("%x", b)
}

func (h *UserHandler) Start() {
	go func() {
		for {
			h.store.Sync(h.ctx)
		}
	}()
}

func (h *UserHandler) Save(v interface{}) error {
	if err := h.store.Put(h.ctx, v); err != nil {
		return fmt.Errorf("failed: %v", err)
	}
	return errors.New("Save incomplete!")
}
