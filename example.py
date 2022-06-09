import ISGFormatHandler as handler

isg_file_path = 'example/model.isg'  # EDIT THIS LINE
output_path = 'example'

model = handler.Model()
model.retrieveByPath(isg_file_path)

# Plot the model
model.plot()

# The possible formats are 'isg1.01', 'isg2.00', 'csv', 'gsf', 'tif', 'gri'
model.convertTo(output_path, 'isg1.01')
