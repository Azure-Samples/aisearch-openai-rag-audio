import React, { useState } from "react";
import * as Form from "@radix-ui/react-form";

const CustomerForm = () => {
    const currentDateTime = new Date().toISOString().slice(0, 16); // Current date and time in 'YYYY-MM-DDTHH:mm' format

    const [formValues, setFormValues] = useState({
        email: "",
        contact: "",
        loan: "",
        balance: "",
        installment: "",
        nextInstallmentDate: "",
        currentDateTime: currentDateTime,
        comment: ""
    });

    // Handle form submission
    const handleSubmit = async (event: { preventDefault: () => void }) => {
        event.preventDefault(); // Prevent the default form submission
        try {
            const response = await fetch("https://your-backend-api.com/submit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formValues)
            });

            if (response.ok) {
                alert("Form submitted successfully!");
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.message}`);
            }
        } catch (error) {
            alert("An error occurred while submitting the form.");
            console.error("Error submitting form:", error);
        }
    };

    // Handle input changes
    const handleChange = (e: { target: { name: any; value: any } }) => {
        const { name, value } = e.target;
        setFormValues(prevValues => ({
            ...prevValues,
            [name]: value
        }));
    };

    return (
        <Form.Root className="FormRoot mx-auto max-h-screen w-full max-w-lg overflow-hidden rounded-none bg-white shadow-md" onSubmit={handleSubmit}>
            <div className="max-h-[90vh] overflow-y-auto p-6">
                <h1 className="pb-3 text-xl">Filled the User Information</h1>
                {/* User Email */}
                <Form.Field className="FormField mb-4 flex flex-col" name="email">
                    <Form.Label className="FormLabel mb-1 text-sm font-semibold text-gray-700">Email</Form.Label>
                    <Form.Control asChild>
                        <input
                            className="Input w-full rounded-md border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
                            type="email"
                            name="email"
                            value={formValues.email}
                            onChange={handleChange}
                            required
                        />
                    </Form.Control>
                    <Form.Message className="FormMessage mt-1 text-sm text-red-500" match="valueMissing">
                        Please enter your email
                    </Form.Message>
                    <Form.Message className="FormMessage mt-1 text-sm text-red-500" match="typeMismatch">
                        Please provide a valid email
                    </Form.Message>
                </Form.Field>

                {/* User Contact Mobile Number */}
                <Form.Field className="FormField mb-4 flex flex-col" name="contact">
                    <Form.Label className="FormLabel mb-1 text-sm font-semibold text-gray-700">Contact Number</Form.Label>
                    <Form.Control asChild>
                        <input
                            className="Input w-full rounded-md border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
                            type="tel"
                            name="contact"
                            value={formValues.contact}
                            onChange={handleChange}
                            required
                        />
                    </Form.Control>
                    <Form.Message className="FormMessage mt-1 text-sm text-red-500" match="valueMissing">
                        Please enter your contact number
                    </Form.Message>
                </Form.Field>

                {/* Outstanding Balance */}
                <Form.Field className="FormField mb-4 flex flex-col" name="balance">
                    <Form.Label className="FormLabel mb-1 text-sm font-semibold text-gray-700">Total Loan Value</Form.Label>
                    <Form.Control asChild>
                        <input
                            className="Input w-full rounded-md border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
                            type="number"
                            step="0.01"
                            name="balance"
                            value={formValues.loan}
                            onChange={handleChange}
                            required
                        />
                    </Form.Control>
                    <Form.Message className="FormMessage mt-1 text-sm text-red-500" match="valueMissing">
                        Please enter the total loan balance
                    </Form.Message>
                </Form.Field>

                {/* Outstanding Balance */}
                <Form.Field className="FormField mb-4 flex flex-col" name="balance">
                    <Form.Label className="FormLabel mb-1 text-sm font-semibold text-gray-700">Outstanding Balance</Form.Label>
                    <Form.Control asChild>
                        <input
                            className="Input w-full rounded-md border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
                            type="number"
                            step="0.01"
                            name="balance"
                            value={formValues.balance}
                            onChange={handleChange}
                            required
                        />
                    </Form.Control>
                    <Form.Message className="FormMessage mt-1 text-sm text-red-500" match="valueMissing">
                        Please enter the outstanding balance
                    </Form.Message>
                </Form.Field>

                {/* Upcoming Installment Payment */}
                <Form.Field className="FormField mb-4 flex flex-col" name="installment">
                    <Form.Label className="FormLabel mb-1 text-sm font-semibold text-gray-700">Upcoming Installment</Form.Label>
                    <Form.Control asChild>
                        <input
                            className="Input w-full rounded-md border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
                            type="number"
                            step="0.01"
                            name="installment"
                            value={formValues.installment}
                            onChange={handleChange}
                            required
                        />
                    </Form.Control>
                    <Form.Message className="FormMessage mt-1 text-sm text-red-500" match="valueMissing">
                        Please enter the upcoming installment amount
                    </Form.Message>
                </Form.Field>

                {/* Next Installment Payment Schedule Date */}
                <Form.Field className="FormField mb-4 flex flex-col" name="nextInstallmentDate">
                    <Form.Label className="FormLabel mb-1 text-sm font-semibold text-gray-700">Next Installment Date</Form.Label>
                    <Form.Control asChild>
                        <input
                            className="Input w-full rounded-md border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
                            type="date"
                            name="nextInstallmentDate"
                            value={formValues.nextInstallmentDate}
                            onChange={handleChange}
                            required
                        />
                    </Form.Control>
                </Form.Field>

                {/* Today's Date and Time */}
                <Form.Field className="FormField mb-4 flex flex-col" name="currentDateTime">
                    <Form.Label className="FormLabel mb-1 text-sm font-semibold text-gray-700">Today's Date and Time</Form.Label>
                    <Form.Control asChild>
                        <input
                            className="Input w-full rounded-md border border-gray-300 bg-gray-100 p-3 focus:outline-none"
                            type="datetime-local"
                            name="currentDateTime"
                            value={formValues.currentDateTime}
                            disabled
                        />
                    </Form.Control>
                </Form.Field>

                {/* Additional Comment */}
                <Form.Field className="FormField mb-4 flex flex-col" name="comment">
                    <Form.Label className="FormLabel mb-1 text-sm font-semibold text-gray-700">Additional Comment</Form.Label>
                    <Form.Control asChild>
                        <textarea
                            className="Textarea w-full rounded-md border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
                            name="comment"
                            value={formValues.comment}
                            onChange={handleChange}
                        />
                    </Form.Control>
                </Form.Field>
            </div>

            <div className="max-h-[10vh] bg-white px-6 pb-10 pt-3">
                {/* Submit Button */}
                <Form.Submit asChild>
                    <button className="Button w-full rounded-md bg-blue-500 py-3 font-bold text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400">
                        Submit
                    </button>
                </Form.Submit>
            </div>
        </Form.Root>
    );
};

export default CustomerForm;
