"""Actual C3D10 results, displayed on corner tetrahedra with labelled limits."""
from pathlib import Path
import numpy as np,json,importlib.util
ROOT=Path(__file__).resolve().parents[2]
def main():
 spec=importlib.util.spec_from_file_location('rr',ROOT/'cad/rebuild_r3_2/render.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
 import vtk
 from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
 from PIL import Image,ImageDraw,ImageFont
 report=json.loads((ROOT/'reports/l2_revision/fem_F1H.json').read_text());w=ROOT.parent/('_support/work/l2/fem/F1H/h1.8_'+report['source_step_sha256'][:10]);z=np.load(w/'mesh_arrays.npz');xyz=z['xyz'];conn=z['conn'];ids=z['node_ids'];eids=z['element_ids']
 # Arrays store node positions by index; explicitly verify before use.
 if conn.max()>=len(xyz):conn=np.searchsorted(ids,conn)
 cells=conn[:,:4];out=ROOT/'views/l2_revision/F1H';out.mkdir(parents=True,exist_ok=True)
 for case in report['levels'][-1]['cases']:
  name=case['case']['name'];a=np.load(w/name/'result_arrays.npz');ui=np.searchsorted(a['node_ids'],ids);u=a['displacement_mm'][ui];ei=np.searchsorted(eids,a['stress_element_ids']);sv=np.bincount(ei,weights=a['von_mises_MPa'],minlength=len(eids))/np.maximum(np.bincount(ei,minlength=len(eids)),1)
  for mode in ['stress','displacement'] if name.startswith('LC4') else ['stress']:
   values=np.linalg.norm(u,axis=1)
   if mode=='stress':
    accum=np.bincount(cells.ravel(),weights=np.repeat(sv,4),minlength=len(xyz));counts=np.bincount(cells.ravel(),minlength=len(xyz));values=accum/np.maximum(counts,1)
   pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(xyz,deep=True));grid=vtk.vtkUnstructuredGrid();grid.SetPoints(pts);ca=vtk.vtkCellArray();data=np.column_stack([np.full(len(cells),4),cells]).ravel().astype(np.int64);ca.SetCells(len(cells),numpy_to_vtkIdTypeArray(data,deep=True));grid.SetCells(vtk.VTK_TETRA,ca)
   vals=numpy_to_vtk(values,deep=True);vals.SetName(mode);grid.GetPointData().SetScalars(vals)
   lut=vtk.vtkLookupTable();lut.SetHueRange(.667,0);lut.SetNumberOfTableValues(256);limit=case['volume_weighted_P99_vm_MPa']*1.5 if mode=='stress' else float(values.max());lut.SetRange(0,limit);lut.Build()
   mapper=vtk.vtkDataSetMapper();mapper.SetInputData(grid);mapper.SetLookupTable(lut);mapper.SetScalarRange(0,limit);actor=vtk.vtkActor();actor.SetMapper(mapper)
   ren=vtk.vtkRenderer();ren.SetBackground(.96,.97,.98);ren.AddActor(actor);bar=vtk.vtkScalarBarActor();bar.SetLookupTable(lut);bar.SetTitle('MPa' if mode=='stress' else 'mm');bar.SetPosition(.86,.16);bar.SetWidth(.1);bar.SetHeight(.63);bar.GetLabelTextProperty().SetColor(.1,.2,.3);bar.GetTitleTextProperty().SetColor(.1,.2,.3);ren.AddActor2D(bar)
   cam=ren.GetActiveCamera();cam.SetPosition(125,-95,125);cam.SetFocalPoint(0,44,15);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(57);ren.ResetCameraClippingRange();win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.AddRenderer(ren);win.SetSize(1500,1200);win.Render();capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.Update();png=out/(name[:3]+'_'+mode+'.png');wr=vtk.vtkPNGWriter();wr.SetFileName(str(png));wr.SetInputConnection(capture.GetOutputPort());wr.Write();win.Finalize()
   im=Image.open(png);draw=ImageDraw.Draw(im);font=lambda sz:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',sz);draw.rectangle((0,0,1500,130),fill='#f8fafb');draw.text((40,22),'F1H / '+name+' / '+mode,font=font(29),fill='#203f50');draw.text((40,76),'实际 CalculiX C3D10 结果；未放大变形；角节点平均显示；热点超色标上限饱和',font=font(22),fill='#586b76');draw.rectangle((0,1100,1500,1200),fill='#f8fafb');draw.text((40,1130),f'E1700 MPa / ν0.37 假设；最大位移 {case["maximum_displacement_mm"]:.5f} mm；并非实物强度认证',font=font(23),fill='#455b68');im.save(png)
 print('Actual FEM images rendered',flush=True)
if __name__=='__main__':main()
