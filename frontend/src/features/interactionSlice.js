import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  hcp_name: "",
  interaction_type: "",
  date: "",
  time: "",
  topics: [],
  materials_shared: [],
  sentiment: "",
  attendees: [],
};

const interactionSlice = createSlice({
  name: "interaction",
  initialState,
  reducers: {
    updateFields: (state, action) => {
      return { ...state, ...action.payload };
    },
    resetForm: () => initialState,
  },
});

export const { updateFields, resetForm } = interactionSlice.actions;
export default interactionSlice.reducer;
