/**
 * Component tests for ServiceUnavailable
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ServiceUnavailable } from "./ServiceUnavailable";

describe("ServiceUnavailable", () => {
  it("renders the service name in the heading", () => {
    render(<ServiceUnavailable serviceName="Search" />);

    expect(
      screen.getByText("Search is temporarily unavailable"),
    ).toBeInTheDocument();
  });

  it("displays navigation links", () => {
    render(<ServiceUnavailable serviceName="API" />);

    expect(screen.getByText("Browse articles")).toBeInTheDocument();
    expect(screen.getByText("Engineering posts")).toBeInTheDocument();
    expect(screen.getByText("Homepage")).toBeInTheDocument();
  });

  it("has correct link hrefs", () => {
    render(<ServiceUnavailable serviceName="Test Service" />);

    expect(screen.getByText("Browse articles").closest("a")).toHaveAttribute(
      "href",
      "/blog",
    );
    expect(screen.getByText("Engineering posts").closest("a")).toHaveAttribute(
      "href",
      "/engineering",
    );
    expect(screen.getByText("Homepage").closest("a")).toHaveAttribute(
      "href",
      "/",
    );
  });

  it("applies custom className", () => {
    const { container } = render(
      <ServiceUnavailable serviceName="Test" className="custom-class" />,
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });
});
